/**
 * SMSRadarPanel.jsx - Panel Radar de Reportes SMS
 * =================================================
 * Visualización estilo "Radar de Tráfico" para reportes de seguridad
 * con códigos de color ICAO (Crítico/Alto/Medio/Bajo)
 * 
 * @component
 * @author OnTrackia Dev Team
 */

import { useState, useEffect } from 'react';
import { AlertTriangle, Shield, Clock, User, ChevronRight, RefreshCw, CheckCircle, Eye } from 'lucide-react';

const SMSRadarPanel = ({ onReportClick }) => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);

    const fetchReports = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v2/sms/reports');
            if (response.ok) {
                const data = await response.json();
                setReports(data);
                setLastUpdate(new Date().toLocaleTimeString());
            }
        } catch (error) {
            console.error('Error fetching SMS reports:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchReports();
        // Polling every 30 seconds
        const interval = setInterval(fetchReports, 30000);
        return () => clearInterval(interval);
    }, []);

    const getRiskColor = (level) => {
        switch (level) {
            case 'CRITICAL': return { bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444', text: '#ef4444' };
            case 'HIGH': return { bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b', text: '#f59e0b' };
            case 'MEDIUM': return { bg: 'rgba(234, 179, 8, 0.15)', border: '#eab308', text: '#eab308' };
            case 'LOW': return { bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981', text: '#10b981' };
            default: return { bg: 'var(--glass-bg)', border: 'var(--glass-border)', text: 'var(--text-secondary)' };
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'OPEN':
                return { label: 'ABIERTO', color: '#ef4444', icon: AlertTriangle };
            case 'REVIEWING':
                return { label: 'EN REVISIÓN', color: '#f59e0b', icon: Eye };
            case 'CLOSED':
                return { label: 'CERRADO', color: '#10b981', icon: CheckCircle };
            default:
                return { label: status, color: 'var(--text-muted)', icon: Clock };
        }
    };

    const getSourceLabel = (source) => {
        switch (source) {
            case 'AUDIT_AUTO': return '🤖 Auto-Auditoría';
            case 'VOLUNTARY_ANONYMOUS': return '📢 Reporte Anónimo';
            case 'SUPERVISOR_MANUAL': return '👤 Supervisor';
            default: return source;
        }
    };

    const openReports = reports.filter(r => r.status === 'OPEN');

    return (
        <div className="glass-card" style={{
            padding: '0',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden'
        }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '16px 20px',
                borderBottom: '1px solid var(--glass-border)',
                background: openReports.length > 0 ? 'rgba(239, 68, 68, 0.05)' : 'transparent'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Shield size={18} color={openReports.length > 0 ? '#ef4444' : 'var(--info)'} />
                    <span style={{
                        fontSize: '13px',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        color: 'var(--text-primary)'
                    }}>
                        Radar SMS
                    </span>
                    {openReports.length > 0 && (
                        <span style={{
                            background: '#ef4444',
                            color: '#fff',
                            fontSize: '11px',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '10px'
                        }}>
                            {openReports.length} ABIERTOS
                        </span>
                    )}
                </div>
                <button
                    onClick={fetchReports}
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '11px'
                    }}
                >
                    <RefreshCw size={14} className={loading ? 'spin' : ''} />
                    {lastUpdate && <span>{lastUpdate}</span>}
                </button>
            </div>

            {/* Reports List */}
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {reports.length === 0 ? (
                    <div style={{
                        padding: '40px 20px',
                        textAlign: 'center',
                        color: 'var(--text-muted)'
                    }}>
                        <Shield size={32} style={{ opacity: 0.3, marginBottom: '10px' }} />
                        <p style={{ fontSize: '13px' }}>Sin reportes de seguridad activos</p>
                        <p style={{ fontSize: '11px', marginTop: '4px' }}>
                            El sistema está operando normalmente
                        </p>
                    </div>
                ) : (
                    reports.slice(0, 5).map((report, index) => {
                        const riskStyle = getRiskColor(report.risk_level);
                        const statusInfo = getStatusBadge(report.status);
                        const StatusIcon = statusInfo.icon;
                        const isCriticalOpen = report.risk_level === 'CRITICAL' && report.status === 'OPEN';

                        return (
                            <div
                                key={report.id}
                                onClick={() => onReportClick && onReportClick(report)}
                                className={isCriticalOpen ? 'critical-blink' : ''}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px',
                                    padding: '14px 20px',
                                    borderBottom: index < reports.length - 1 ? '1px solid var(--glass-border)' : 'none',
                                    background: riskStyle.bg,
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    animation: isCriticalOpen ? 'criticalPulse 1.5s ease-in-out infinite' : 'none'
                                }}
                            >
                                {/* Risk Indicator */}
                                <div style={{
                                    width: '8px',
                                    height: '40px',
                                    background: riskStyle.border,
                                    borderRadius: '4px'
                                }} />

                                {/* Content */}
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        marginBottom: '4px'
                                    }}>
                                        <span style={{
                                            fontSize: '12px',
                                            fontWeight: 700,
                                            fontFamily: 'var(--font-mono)',
                                            color: riskStyle.text
                                        }}>
                                            {report.id}
                                        </span>
                                        <span style={{
                                            fontSize: '10px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '4px',
                                            color: statusInfo.color
                                        }}>
                                            <StatusIcon size={12} />
                                            {statusInfo.label}
                                        </span>
                                    </div>

                                    <p style={{
                                        fontSize: '12px',
                                        color: 'var(--text-primary)',
                                        margin: 0,
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap'
                                    }}>
                                        {report.description.slice(0, 60)}...
                                    </p>

                                    <div style={{
                                        display: 'flex',
                                        gap: '12px',
                                        marginTop: '6px',
                                        fontSize: '10px',
                                        color: 'var(--text-muted)'
                                    }}>
                                        <span>{getSourceLabel(report.source)}</span>
                                        <span>•</span>
                                        <span style={{ fontFamily: 'var(--font-mono)' }}>
                                            {report.risk_level} (Score: {report.risk_score})
                                        </span>
                                    </div>
                                </div>

                                <ChevronRight size={16} color="var(--text-muted)" />
                            </div>
                        );
                    })
                )}
            </div>

            {/* Footer with matrix reference */}
            {reports.length > 0 && (
                <div style={{
                    padding: '12px 20px',
                    background: 'var(--bg-deep)',
                    borderTop: '1px solid var(--glass-border)',
                    fontSize: '10px',
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                    display: 'flex',
                    justifyContent: 'space-between'
                }}>
                    <span>MATRIZ: ICAO 5x5 | SHA-256 ENABLED</span>
                    <span>TOTAL: {reports.length} reportes</span>
                </div>
            )}
        </div>
    );
};

export default SMSRadarPanel;
