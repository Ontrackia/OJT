/**
 * OnTrackIA OJT V2.0 - Evidence Grid Component
 * =============================================
 * Grid de evidencias con thumbnails WebP y lazy loading
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { MapPin, Clock, AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';

const EvidenceGrid = ({ evidences, onEvidenceSelect, language }) => {
    const getRiskIcon = (riskLevel) => {
        switch (riskLevel) {
            case 'red':
                return <AlertTriangle size={16} color="var(--error)" />;
            case 'yellow':
                return <AlertCircle size={16} color="var(--warning)" />;
            case 'green':
                return <CheckCircle size={16} color="var(--success)" />;
            default:
                return <AlertCircle size={16} color="var(--text-muted)" />;
        }
    };

    const getRiskColor = (riskLevel) => {
        switch (riskLevel) {
            case 'red':
                return 'var(--error)';
            case 'yellow':
                return 'var(--warning)';
            case 'green':
                return 'var(--success)';
            default:
                return 'var(--text-muted)';
        }
    };

    const formatDate = (isoString) => {
        try {
            const date = new Date(isoString);
            return date.toLocaleString(language === 'es' ? 'es-ES' : 'en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return isoString;
        }
    };

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '20px'
        }}>
            {evidences.map((evidence) => (
                <div
                    key={evidence.id}
                    className="glass-card"
                    onClick={() => onEvidenceSelect(evidence)}
                    style={{
                        padding: 0,
                        overflow: 'hidden',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        border: `1px solid ${getRiskColor(evidence.risk_level)}20`
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-4px)';
                        e.currentTarget.style.boxShadow = `0 8px 24px ${getRiskColor(evidence.risk_level)}20`;
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = 'none';
                    }}
                >
                    {/* Thumbnail */}
                    <div style={{
                        position: 'relative',
                        width: '100%',
                        paddingTop: '75%', // 4:3 aspect ratio
                        background: 'var(--bg-deep)',
                        overflow: 'hidden'
                    }}>
                        {evidence.thumbnail_path ? (
                            <img
                                src={evidence.thumbnail_path}
                                alt="Evidence thumbnail"
                                loading="lazy"
                                style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover'
                                }}
                            />
                        ) : (
                            <div style={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                width: '100%',
                                height: '100%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'var(--text-muted)',
                                fontSize: '12px'
                            }}>
                                {language === 'es' ? 'Sin miniatura' : 'No thumbnail'}
                            </div>
                        )}

                        {/* Risk Badge */}
                        <div style={{
                            position: 'absolute',
                            top: '12px',
                            right: '12px',
                            padding: '6px 12px',
                            background: `${getRiskColor(evidence.risk_level)}20`,
                            backdropFilter: 'blur(8px)',
                            border: `1px solid ${getRiskColor(evidence.risk_level)}`,
                            borderRadius: '20px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            fontSize: '11px',
                            fontWeight: 700,
                            color: getRiskColor(evidence.risk_level)
                        }}>
                            {getRiskIcon(evidence.risk_level)}
                            {evidence.risk_level.toUpperCase()}
                        </div>
                    </div>

                    {/* Metadata */}
                    <div style={{ padding: '16px' }}>
                        {/* Task ID */}
                        <div style={{
                            fontSize: '13px',
                            fontWeight: 600,
                            color: 'var(--text-primary)',
                            marginBottom: '8px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                        }}>
                            {evidence.task_id}
                        </div>

                        {/* Technician */}
                        <div style={{
                            fontSize: '12px',
                            color: 'var(--text-secondary)',
                            marginBottom: '12px'
                        }}>
                            {evidence.technician_name}
                        </div>

                        {/* GPS & Timestamp */}
                        <div style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '6px'
                        }}>
                            {evidence.metadata?.gps_latitude && (
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    fontSize: '11px',
                                    color: 'var(--text-muted)'
                                }}>
                                    <MapPin size={12} />
                                    <span>
                                        {evidence.metadata.gps_latitude.toFixed(4)}, {evidence.metadata.gps_longitude.toFixed(4)}
                                    </span>
                                </div>
                            )}

                            {evidence.metadata?.capture_timestamp && (
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    fontSize: '11px',
                                    color: 'var(--text-muted)'
                                }}>
                                    <Clock size={12} />
                                    <span>{formatDate(evidence.metadata.capture_timestamp)}</span>
                                </div>
                            )}
                        </div>

                        {/* Optimization Info */}
                        {evidence.optimization?.reduction_percent && (
                            <div style={{
                                marginTop: '12px',
                                paddingTop: '12px',
                                borderTop: '1px solid var(--glass-border)',
                                fontSize: '10px',
                                color: 'var(--success)',
                                fontWeight: 600
                            }}>
                                {language === 'es' ? 'Optimizado' : 'Optimized'}: {evidence.optimization.reduction_percent}%
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default EvidenceGrid;
