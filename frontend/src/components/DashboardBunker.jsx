/**
 * OnTrackIA OJT V2.0 - Dashboard de Control Búnker
 * =================================================
 * Dashboard principal con estilo Clean Block y Glassmorphism
 * 
 * Features:
 * - Fondo Morado Oscuro (#0a051a)
 * - Tarjetas Glassmorphism
 * - Botones 44x44px (Ergonomía Aeronáutica)
 * - Sync Indicator reactivo
 * - Estadísticas en tiempo real
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';
import { MapPin, FileText, Users, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import SyncIndicator from './SyncIndicator';

const DashboardBunker = () => {
    const [stats, setStats] = useState({
        totalTecnicos: 0,
        tareasAsignadas: 0,
        tareasCompletadas: 0,
        evidenciasSubidas: 0,
        horasTotales: 0,
        tasaCompletitud: 0
    });

    useEffect(() => {
        // Simular carga de estadísticas
        setStats({
            totalTecnicos: 24,
            tareasAsignadas: 186,
            tareasCompletadas: 142,
            evidenciasSubidas: 89,
            horasTotales: 3420,
            tasaCompletitud: 76
        });
    }, []);

    const StatCard = ({ icon: Icon, label, value, trend, color = 'var(--primary)' }) => (
        <div className="glass-card" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
        }}>
            <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '12px',
                background: `linear-gradient(135deg, ${color}, ${color}dd)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: `0 4px 12px ${color}40`
            }}>
                <Icon size={32} color="white" />
            </div>
            <div style={{ flex: 1 }}>
                <div className="stat-label">{label}</div>
                <div className="stat-value" style={{ color }}>{value}</div>
                {trend && (
                    <div style={{
                        fontSize: '12px',
                        color: trend >= 0 ? 'var(--success)' : 'var(--error)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        marginTop: '4px'
                    }}>
                        <TrendingUp size={14} />
                        {trend >= 0 ? '+' : ''}{trend}% vs mes anterior
                    </div>
                )}
            </div>
        </div>
    );

    const QuickAction = ({ icon: Icon, label, onClick }) => (
        <button className="icon-button" onClick={onClick} title={label} style={{
            flexDirection: 'column',
            width: '80px',
            height: '80px',
            gap: '8px'
        }}>
            <Icon size={24} />
            <span style={{ fontSize: '11px', textAlign: 'center' }}>{label}</span>
        </button>
    );

    return (
        <div style={{
            minHeight: '100vh',
            background: 'var(--bg-deep)',
            padding: '24px'
        }}>
            {/* Header */}
            <header style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '32px',
                padding: '16px 24px',
                background: 'var(--glass-bg)',
                backdropFilter: 'blur(10px)',
                border: '1px solid var(--glass-border)',
                borderRadius: '12px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                        width: '48px',
                        height: '48px',
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, var(--primary), var(--primary-hover))',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: '0 4px 12px rgba(124, 58, 237, 0.4)'
                    }}>
                        <span style={{ fontSize: '24px' }}>🔐</span>
                    </div>
                    <div>
                        <h1 style={{
                            fontSize: '24px',
                            fontWeight: 700,
                            marginBottom: '4px'
                        }}>
                            OnTrackIA OJT - Dashboard Búnker
                        </h1>
                        <p style={{
                            fontSize: '14px',
                            color: 'var(--text-secondary)'
                        }}>
                            Trazabilidad Ultimate con Geolocalización Forense
                        </p>
                    </div>
                </div>

                <SyncIndicator />
            </header>

            {/* Stats Grid */}
            <div className="stats-grid" style={{ marginBottom: '32px' }}>
                <StatCard
                    icon={Users}
                    label="Técnicos Activos"
                    value={stats.totalTecnicos}
                    trend={12}
                    color="#10b981"
                />
                <StatCard
                    icon={FileText}
                    label="Tareas Asignadas"
                    value={stats.tareasAsignadas}
                    trend={8}
                    color="#7c3aed"
                />
                <StatCard
                    icon={CheckCircle}
                    label="Tareas Completadas"
                    value={stats.tareasCompletadas}
                    trend={15}
                    color="#3b82f6"
                />
                <StatCard
                    icon={MapPin}
                    label="Evidencias con GPS"
                    value={stats.evidenciasSubidas}
                    trend={22}
                    color="#f59e0b"
                />
            </div>

            {/* Quick Actions */}
            <div className="glass-card" style={{ marginBottom: '32px' }}>
                <h2 style={{
                    fontSize: '18px',
                    fontWeight: 600,
                    marginBottom: '16px'
                }}>
                    ⚡ Acciones Rápidas
                </h2>
                <div style={{
                    display: 'flex',
                    gap: '16px',
                    flexWrap: 'wrap'
                }}>
                    <QuickAction
                        icon={Users}
                        label="Nuevo Técnico"
                        onClick={() => alert('Crear nuevo técnico')}
                    />
                    <QuickAction
                        icon={FileText}
                        label="Nueva Tarea"
                        onClick={() => alert('Crear nueva tarea OJT')}
                    />
                    <QuickAction
                        icon={MapPin}
                        label="Ver Mapa"
                        onClick={() => alert('Ver mapa de evidencias GPS')}
                    />
                    <QuickAction
                        icon={CheckCircle}
                        label="Validar"
                        onClick={() => alert('Validar tareas pendientes')}
                    />
                </div>
            </div>

            {/* Progress Overview */}
            <div className="glass-card">
                <h2 style={{
                    fontSize: '18px',
                    fontWeight: 600,
                    marginBottom: '16px'
                }}>
                    📊 Progreso General
                </h2>

                <div style={{ margin Bottom: '16px' }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginBottom: '8px'
                    }}>
                        <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                            Completitud Global
                        </span>
                        <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--primary)' }}>
                            {stats.tasaCompletitud}%
                        </span>
                    </div>
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${stats.tasaCompletitud}%` }}
                        />
                    </div>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '16px',
                    marginTop: '24px'
                }}>
                    <div style={{
                        padding: '16px',
                        background: 'rgba(124, 58, 237, 0.05)',
                        border: '1px solid rgba(124, 58, 237, 0.2)',
                        borderRadius: '8px'
                    }}>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                            Horas Totales OJT
                        </div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--primary)' }}>
                            {stats.horasTotales.toLocaleString()}h
                        </div>
                    </div>

                    <div style={{
                        padding: '16px',
                        background: 'rgba(16, 185, 129, 0.05)',
                        border: '1px solid rgba(16, 185, 129, 0.2)',
                        borderRadius: '8px'
                    }}>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                            Tasa de Validación
                        </div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#10b981' }}>
                            94%
                        </div>
                    </div>
                </div>

                {/* Compliance Badges */}
                <div style={{
                    marginTop: '24px',
                    padding: '16px',
                    background: 'rgba(59, 130, 246, 0.05)',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                    borderRadius: '8px'
                }}>
                    <div style={{
                        fontSize: '12px',
                        color: 'var(--text-secondary)',
                        marginBottom: '12px'
                    }}>
                        ✅ Compliance Certificado
                    </div>
                    <div style={{
                        display: 'flex',
                        gap: '8px',
                        flexWrap: 'wrap'
                    }}>
                        {['RAC LPTA 66', 'UK CAA CAP 741', 'AAC F1/F2', 'ICAO Doc 9859'].map(standard => (
                            <span key={standard} style={{
                                padding: '6px 12px',
                                background: 'var(--glass-bg)',
                                border: '1px solid var(--glass-border)',
                                borderRadius: '16px',
                                fontSize: '12px',
                                fontWeight: 600
                            }}>
                                {standard}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardBunker;
