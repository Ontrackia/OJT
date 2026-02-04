/**
 * OnTrackIA OJT V2.0 - Sync Indicator Component
 * ==============================================
 * Indicador de estado de sincronización PWA Offline-First
 * 
 * Estados:
 * - Online (verde): Conectado y sincronizado
 * - Offline (rojo): Sin conexión
 * - Syncing (amarillo): Sincronizando cambios
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';

const SyncIndicator = () => {
    const [syncStatus, setSyncStatus] = useState('online');
    const [lastSync, setLastSync] = useState(null);

    useEffect(() => {
        // Función para actualizar estado de conexión
        const updateOnlineStatus = () => {
            if (navigator.onLine) {
                setSyncStatus('online');
            } else {
                setSyncStatus('offline');
            }
        };

        // Listener para cambios de conexión
        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);

        // Estado inicial
        updateOnlineStatus();

        // Simular sincronización periódica
        const syncInterval = setInterval(() => {
            if (navigator.onLine) {
                setSyncStatus('syncing');

                // Simular sincronización (aquí iría la lógica real)
                setTimeout(() => {
                    setSyncStatus('online');
                    setLastSync(new Date());
                }, 1500);
            }
        }, 30000); // Cada 30 segundos

        return () => {
            window.removeEventListener('online', updateOnlineStatus);
            window.removeEventListener('offline', updateOnlineStatus);
            clearInterval(syncInterval);
        };
    }, []);

    const getStatusText = () => {
        switch (syncStatus) {
            case 'online':
                return 'En línea';
            case 'offline':
                return 'Sin conexión';
            case 'syncing':
                return 'Sincronizando...';
            default:
                return 'Desconocido';
        }
    };

    const getStatusIcon = () => {
        switch (syncStatus) {
            case 'online':
                return '✓';
            case 'offline':
                return '✗';
            case 'syncing':
                return '⟳';
            default:
                return '?';
        }
    };

    return (
        <div className="sync-indicator-container" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '8px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
            <div
                className={`sync-indicator ${syncStatus}`}
                title={getStatusText()}
            />
            <span style={{
                fontSize: '14px',
                color: '#cbd5e1',
                fontWeight: 500
            }}>
                {getStatusIcon()} {getStatusText()}
            </span>
            {lastSync && (
                <span style={{
                    fontSize: '12px',
                    color: '#94a3b8',
                    marginLeft: '8px'
                }}>
                    {lastSync.toLocaleTimeString('es-ES', {
                        hour: '2-digit',
                        minute: '2-digit'
                    })}
                </span>
            )}
        </div>
    );
};

export default SyncIndicator;
