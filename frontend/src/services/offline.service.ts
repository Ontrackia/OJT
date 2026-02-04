/**
 * Offline Service - Network detection and sync management
 */

import { offlineDB } from '../db/indexedDB';

export class OfflineService {
    private isOnline: boolean = navigator.onLine;
    private syncInProgress: boolean = false;
    private listeners: Set<(isOnline: boolean) => void> = new Set();

    constructor() {
        this.initNetworkListeners();
    }

    private initNetworkListeners() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.notifyListeners();
            this.triggerSync();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.notifyListeners();
        });
    }

    onNetworkChange(callback: (isOnline: boolean) => void) {
        this.listeners.add(callback);
        return () => this.listeners.delete(callback);
    }

    private notifyListeners() {
        this.listeners.forEach(callback => callback(this.isOnline));
    }

    getOnlineStatus(): boolean {
        return this.isOnline;
    }

    async triggerSync() {
        if (!this.isOnline || this.syncInProgress) {
            return;
        }

        this.syncInProgress = true;

        try {
            const queue = await offlineDB.getSyncQueue();

            for (const item of queue) {
                try {
                    await this.syncItem(item);
                    await offlineDB.markAsSynced(item.id);
                } catch (error) {
                    console.error(`Failed to sync item ${item.id}:`, error);
                    await offlineDB.incrementAttempts(item.id);
                }
            }
        } finally {
            this.syncInProgress = false;
        }
    }

    private async syncItem(item: any) {
        const token = localStorage.getItem('token');

        const response = await fetch('/api/v2/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-Offline-Timestamp': item.createdAt,
            },
            body: JSON.stringify({
                type: item.type,
                data: item.data,
            }),
        });

        if (!response.ok) {
            throw new Error(`Sync failed: ${response.statusText}`);
        }

        return await response.json();
    }

    async getPendingCount(): Promise<number> {
        return await offlineDB.getPendingCount();
    }

    isSyncing(): boolean {
        return this.syncInProgress;
    }
}

export const offlineService = new OfflineService();
