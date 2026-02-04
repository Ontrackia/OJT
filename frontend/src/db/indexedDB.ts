/**
 * IndexedDB Setup for OnTrackIA V1-Core
 * Offline-first local storage
 */

import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface SyncQueueItem {
    id: string;
    type: 'audit' | 'finding' | 'evidence' | 'sms';
    data: any;
    createdAt: string;
    attempts: number;
    lastAttempt?: string;
    status: 'pending' | 'syncing' | 'synced' | 'failed';
}

interface OnTrackIADB extends DBSchema {
    audits: {
        key: string;
        value: any;
        indexes: { 'by-status': string };
    };
    findings: {
        key: string;
        value: any;
        indexes: { 'by-audit': string };
    };
    evidences: {
        key: string;
        value: any;
        indexes: { 'by-entity': string };
    };
    syncQueue: {
        key: string;
        value: SyncQueueItem;
        indexes: { 'by-status': string };
    };
}

class OfflineDB {
    private db: IDBPDatabase<OnTrackIADB> | null = null;

    async init() {
        this.db = await openDB<OnTrackIADB>('ontrackia-v1', 1, {
            upgrade(db) {
                // Audits store
                const auditStore = db.createObjectStore('audits', { keyPath: 'id' });
                auditStore.createIndex('by-status', 'status');

                // Findings store
                const findingStore = db.createObjectStore('findings', { keyPath: 'id' });
                findingStore.createIndex('by-audit', 'audit_id');

                // Evidences store
                const evidenceStore = db.createObjectStore('evidences', { keyPath: 'id' });
                evidenceStore.createIndex('by-entity', 'entity_id');

                // Sync queue store
                const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id' });
                syncStore.createIndex('by-status', 'status');
            },
        });
    }

    // Audits
    async saveAudit(audit: any) {
        if (!this.db) await this.init();
        await this.db!.put('audits', audit);
        await this.addToSyncQueue('audit', audit);
    }

    async getAudit(id: string) {
        if (!this.db) await this.init();
        return await this.db!.get('audits', id);
    }

    async getAllAudits() {
        if (!this.db) await this.init();
        return await this.db!.getAll('audits');
    }

    // Findings
    async saveFinding(finding: any) {
        if (!this.db) await this.init();
        await this.db!.put('findings', finding);
        await this.addToSyncQueue('finding', finding);
    }

    async getFindingsByAudit(auditId: string) {
        if (!this.db) await this.init();
        return await this.db!.getAllFromIndex('findings', 'by-audit', auditId);
    }

    // Evidences
    async saveEvidence(evidence: any) {
        if (!this.db) await this.init();
        await this.db!.put('evidences', evidence);
        await this.addToSyncQueue('evidence', evidence);
    }

    // Sync Queue
    async addToSyncQueue(type: SyncQueueItem['type'], data: any) {
        if (!this.db) await this.init();

        const item: SyncQueueItem = {
            id: `${type}-${data.id}-${Date.now()}`,
            type,
            data,
            createdAt: new Date().toISOString(),
            attempts: 0,
            status: 'pending',
        };

        await this.db!.put('syncQueue', item);
    }

    async getSyncQueue() {
        if (!this.db) await this.init();
        return await this.db!.getAllFromIndex('syncQueue', 'by-status', 'pending');
    }

    async markAsSynced(id: string) {
        if (!this.db) await this.init();
        const item = await this.db!.get('syncQueue', id);
        if (item) {
            item.status = 'synced';
            await this.db!.put('syncQueue', item);
        }
    }

    async incrementAttempts(id: string) {
        if (!this.db) await this.init();
        const item = await this.db!.get('syncQueue', id);
        if (item) {
            item.attempts += 1;
            item.lastAttempt = new Date().toISOString();
            item.status = item.attempts >= 3 ? 'failed' : 'pending';
            await this.db!.put('syncQueue', item);
        }
    }

    async getPendingCount() {
        if (!this.db) await this.init();
        const pending = await this.db!.getAllFromIndex('syncQueue', 'by-status', 'pending');
        return pending.length;
    }
}

export const offlineDB = new OfflineDB();
