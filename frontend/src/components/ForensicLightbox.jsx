/**
 * OnTrackIA OJT V2.0 - Forensic Lightbox Component
 * =================================================
 * Modal con imagen completa y metadata forense
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { X, MapPin, Clock, Hash, Copy, ExternalLink } from 'lucide-react';
import { useState } from 'react';

const ForensicLightbox = ({ evidence, onClose, language, renderSidePanel }) => {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const openInMaps = () => {
        const lat = evidence.metadata?.gps_latitude;
        const lng = evidence.metadata?.gps_longitude;
        if (lat && lng) {
            window.open(`https://www.google.com/maps?q=${lat},${lng}`, '_blank');
        }
    };

    const formatDateTime = (isoString) => {
        try {
            const date = new Date(isoString);
            return date.toLocaleString(language === 'es' ? 'es-ES' : 'en-US', {
                dateStyle: 'long',
                timeStyle: 'medium'
            });
        } catch {
            return isoString;
        }
    };

    return (
        <div
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(10, 5, 26, 0.95)',
                backdropFilter: 'blur(8px)',
                zIndex: 9999,
                display: 'flex',
                padding: '24px',
                gap: '24px'
            }}
            onClick={onClose}
        >
            {/* Main Image Area */}
            <div
                style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '16px'
                }}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="btn"
                    style={{
                        alignSelf: 'flex-end',
                        width: '44px',
                        height: '44px',
                        padding: 0,
                        background: 'var(--bg-card)',
                        border: '1px solid var(--glass-border)'
                    }}
                >
                    <X size={20} />
                </button>

                {/* Image */}
                <div
                    className="glass-card"
                    style={{
                        flex: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '24px',
                        background: 'var(--bg-card)'
                    }}
                >
                    <img
                        src={evidence.full_image_path}
                        alt="Evidence full resolution"
                        style={{
                            maxWidth: '100%',
                            maxHeight: '100%',
                            objectFit: 'contain',
                            borderRadius: '8px'
                        }}
                    />
                </div>

                {/* Forensic Metadata */}
                <div
                    className="glass-card"
                    style={{
                        padding: '20px',
                        background: 'var(--bg-card)'
                    }}
                >
                    <h3 style={{
                        fontSize: '16px',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        marginBottom: '16px'
                    }}>
                        {language === 'es' ? 'Metadata Forense' : 'Forensic Metadata'}
                    </h3>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '16px'
                    }}>
                        {/* SHA-256 Hash */}
                        <MetadataItem
                            icon={<Hash size={16} />}
                            label="SHA-256"
                            value={evidence.metadata?.server_hash}
                            copyable
                            onCopy={() => copyToClipboard(evidence.metadata?.server_hash)}
                            copied={copied}
                        />

                        {/* GPS Coordinates */}
                        {evidence.metadata?.gps_latitude && (
                            <MetadataItem
                                icon={<MapPin size={16} />}
                                label="GPS"
                                value={`${evidence.metadata.gps_latitude.toFixed(6)}, ${evidence.metadata.gps_longitude.toFixed(6)}`}
                                action={
                                    <button
                                        onClick={openInMaps}
                                        style={{
                                            background: 'none',
                                            border: 'none',
                                            color: 'var(--primary)',
                                            cursor: 'pointer',
                                            padding: '4px'
                                        }}
                                        title={language === 'es' ? 'Abrir en Google Maps' : 'Open in Google Maps'}
                                    >
                                        <ExternalLink size={14} />
                                    </button>
                                }
                            />
                        )}

                        {/* Timestamp */}
                        {evidence.metadata?.capture_timestamp && (
                            <MetadataItem
                                icon={<Clock size={16} />}
                                label={language === 'es' ? 'Capturado' : 'Captured'}
                                value={formatDateTime(evidence.metadata.capture_timestamp)}
                            />
                        )}

                        {/* Device Info */}
                        {evidence.metadata?.device_info && (
                            <MetadataItem
                                icon={<Hash size={16} />}
                                label={language === 'es' ? 'Dispositivo' : 'Device'}
                                value={evidence.metadata.device_info.platform || 'Unknown'}
                            />
                        )}
                    </div>

                    {/* Optimization Info */}
                    {evidence.optimization && (
                        <div style={{
                            marginTop: '16px',
                            paddingTop: '16px',
                            borderTop: '1px solid var(--glass-border)',
                            display: 'flex',
                            gap: '24px',
                            fontSize: '12px',
                            color: 'var(--text-secondary)'
                        }}>
                            <div>
                                <span style={{ color: 'var(--text-muted)' }}>
                                    {language === 'es' ? 'Original:' : 'Original:'}
                                </span>{' '}
                                {evidence.optimization.original_size_mb}MB
                            </div>
                            <div>
                                <span style={{ color: 'var(--text-muted)' }}>
                                    {language === 'es' ? 'Optimizado:' : 'Optimized:'}
                                </span>{' '}
                                {evidence.optimization.optimized_size_kb}KB
                            </div>
                            <div style={{ color: 'var(--success)', fontWeight: 600 }}>
                                {language === 'es' ? 'Reducción:' : 'Reduction:'} {evidence.optimization.reduction_percent}%
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Side Panel (Senior Auditor Coach) */}
            {renderSidePanel && (
                <div
                    style={{
                        width: '420px',
                        flexShrink: 0
                    }}
                    onClick={(e) => e.stopPropagation()}
                >
                    {renderSidePanel()}
                </div>
            )}
        </div>
    );
};

// Componente auxiliar: Metadata Item
const MetadataItem = ({ icon, label, value, copyable, onCopy, copied, action }) => (
    <div>
        <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginBottom: '6px',
            fontSize: '11px',
            fontWeight: 600,
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
        }}>
            {icon}
            <span>{label}</span>
        </div>
        <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            color: 'var(--text-primary)',
            fontFamily: copyable ? 'monospace' : 'inherit',
            wordBreak: 'break-all'
        }}>
            <span style={{ flex: 1 }}>{value}</span>
            {copyable && (
                <button
                    onClick={onCopy}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: copied ? 'var(--success)' : 'var(--primary)',
                        cursor: 'pointer',
                        padding: '4px'
                    }}
                    title={copied ? 'Copied!' : 'Copy'}
                >
                    <Copy size={14} />
                </button>
            )}
            {action}
        </div>
    </div>
);

export default ForensicLightbox;
