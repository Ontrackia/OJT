/**
 * GlassCockpitPanel.jsx
 * =====================
 * Panel "Vista de Pájaro" para el Auditor Senior
 * 
 * Muestra:
 * - Contadores de Findings por Nivel (1/2/3)
 * - Reloj de Arena (alarmas de fechas límite)
 * - Progreso de auditoría actual
 */

import { useState, useEffect } from 'react';
import { AlertTriangle, Clock, Target, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';

const GlassCockpitPanel = ({ onFindingClick }) => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);

    const fetchStats = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v2/audit/dashboard-stats');
            if (response.ok) {
                const data = await response.json();
                setStats(data);
                setLastUpdate(new Date().toLocaleTimeString());
            }
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
        // Polling cada 30 segundos
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
                <RefreshCw size={24} className="animate-spin" style={{ color: 'var(--primary-500)' }} />
                <p style={{ marginTop: '12px', color: 'var(--text-secondary)' }}>Cargando Glass Cockpit...</p>
            </div>
        );
    }

    const getUrgencyIcon = (urgency) => {
        switch (urgency) {
            case 'VENCIDO': return <AlertCircle size={14} />;
            case 'CRÍTICO': return <AlertTriangle size={14} />;
            case 'URGENTE': return <Clock size={14} />;
            default: return <CheckCircle2 size={14} />;
        }
    };

    return (
        <div className="glass-card" style={{
            padding: '20px',
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98))',
            border: '1px solid rgba(139, 92, 246, 0.3)'
        }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Target size={20} style={{ color: '#8b5cf6' }} />
                    <span style={{ fontSize: '14px', fontWeight: 600, letterSpacing: '1px', color: 'var(--text-primary)' }}>
                        GLASS COCKPIT
                    </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <button onClick={fetchStats} style={{
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        padding: '4px'
                    }}>
                        <RefreshCw size={14} style={{ color: 'var(--text-secondary)' }} />
                    </button>
                    <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>⏱ {lastUpdate}</span>
                </div>
            </div>

            {/* Contadores de Findings */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '12px',
                marginBottom: '20px'
            }}>
                {/* Nivel 1 - Crítico */}
                <div style={{
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid rgba(239, 68, 68, 0.4)',
                    borderRadius: '12px',
                    padding: '16px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                }} onClick={() => onFindingClick && onFindingClick(1)}>
                    <div style={{
                        fontSize: '32px',
                        fontWeight: 700,
                        color: '#ef4444',
                        lineHeight: 1
                    }}>
                        {stats?.findings_by_level?.level_1?.count || 0}
                    </div>
                    <div style={{ marginTop: '8px', fontSize: '11px', color: '#ef4444', fontWeight: 600 }}>
                        NIVEL 1
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '2px' }}>
                        Crítico/AOG
                    </div>
                </div>

                {/* Nivel 2 - Mayor */}
                <div style={{
                    background: 'rgba(249, 115, 22, 0.15)',
                    border: '1px solid rgba(249, 115, 22, 0.4)',
                    borderRadius: '12px',
                    padding: '16px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                }} onClick={() => onFindingClick && onFindingClick(2)}>
                    <div style={{
                        fontSize: '32px',
                        fontWeight: 700,
                        color: '#f97316',
                        lineHeight: 1
                    }}>
                        {stats?.findings_by_level?.level_2?.count || 0}
                    </div>
                    <div style={{ marginTop: '8px', fontSize: '11px', color: '#f97316', fontWeight: 600 }}>
                        NIVEL 2
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '2px' }}>
                        Mayor
                    </div>
                </div>

                {/* Nivel 3 - Observación */}
                <div style={{
                    background: 'rgba(234, 179, 8, 0.15)',
                    border: '1px solid rgba(234, 179, 8, 0.4)',
                    borderRadius: '12px',
                    padding: '16px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                }} onClick={() => onFindingClick && onFindingClick(3)}>
                    <div style={{
                        fontSize: '32px',
                        fontWeight: 700,
                        color: '#eab308',
                        lineHeight: 1
                    }}>
                        {stats?.findings_by_level?.level_3?.count || 0}
                    </div>
                    <div style={{ marginTop: '8px', fontSize: '11px', color: '#eab308', fontWeight: 600 }}>
                        NIVEL 3
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '2px' }}>
                        Observación
                    </div>
                </div>
            </div>

            {/* Reloj de Arena - Deadlines */}
            <div style={{
                background: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '8px',
                padding: '14px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <Clock size={14} style={{ color: 'var(--text-secondary)' }} />
                    <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.5px' }}>
                        RELOJ DE ARENA - VENCIMIENTOS
                    </span>
                </div>

                {stats?.deadlines?.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {stats.deadlines.map((deadline, idx) => (
                            <div key={idx} style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '8px 12px',
                                background: deadline.color === 'red' ? 'rgba(239, 68, 68, 0.1)' :
                                    deadline.color === 'orange' ? 'rgba(249, 115, 22, 0.1)' :
                                        'rgba(34, 197, 94, 0.1)',
                                border: `1px solid ${deadline.color === 'red' ? 'rgba(239, 68, 68, 0.3)' :
                                    deadline.color === 'orange' ? 'rgba(249, 115, 22, 0.3)' :
                                        'rgba(34, 197, 94, 0.3)'}`,
                                borderRadius: '6px'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <span style={{
                                        color: deadline.color === 'red' ? '#ef4444' :
                                            deadline.color === 'orange' ? '#f97316' : '#22c55e'
                                    }}>
                                        {getUrgencyIcon(deadline.urgency)}
                                    </span>
                                    <div>
                                        <div style={{ fontSize: '12px', color: 'var(--text-primary)', fontWeight: 500 }}>
                                            {deadline.finding_id} - {deadline.title}
                                        </div>
                                        <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>
                                            Nivel {deadline.level} · {deadline.deadline}
                                        </div>
                                    </div>
                                </div>
                                <div style={{
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '10px',
                                    fontWeight: 700,
                                    color: deadline.color === 'red' ? '#ef4444' :
                                        deadline.color === 'orange' ? '#f97316' : '#22c55e',
                                    background: deadline.color === 'red' ? 'rgba(239, 68, 68, 0.2)' :
                                        deadline.color === 'orange' ? 'rgba(249, 115, 22, 0.2)' :
                                            'rgba(34, 197, 94, 0.2)'
                                }}>
                                    {deadline.days_remaining < 0 ? `${Math.abs(deadline.days_remaining)}d VENCIDO` :
                                        deadline.days_remaining === 0 ? 'HOY' :
                                            `${deadline.days_remaining}d`}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', padding: '16px', color: 'var(--text-tertiary)', fontSize: '12px' }}>
                        ✅ Sin vencimientos próximos
                    </div>
                )}
            </div>

            {/* Progress Bar */}
            <div style={{ marginTop: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Progreso Auditoría</span>
                    <span style={{ fontSize: '11px', color: '#8b5cf6', fontWeight: 600 }}>{stats?.audit_progress || 0}%</span>
                </div>
                <div style={{
                    height: '6px',
                    background: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '3px',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        height: '100%',
                        width: `${stats?.audit_progress || 0}%`,
                        background: 'linear-gradient(90deg, #8b5cf6, #a78bfa)',
                        borderRadius: '3px',
                        transition: 'width 0.5s ease'
                    }} />
                </div>
            </div>

            {/* Footer Stats */}
            <div style={{
                marginTop: '16px',
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '10px',
                color: 'var(--text-tertiary)'
            }}>
                <span>📊 Total Abiertos: {stats?.total_open || 0}</span>
                <span>🚨 SMS Activos: {stats?.sms_reports_open || 0}</span>
            </div>
        </div>
    );
};

export default GlassCockpitPanel;
