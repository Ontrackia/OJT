/**
 * OnTrackIA OJT V2.0 - Senior Auditor Panel Component
 * ====================================================
 * Panel de análisis IA con RAG Multi-Agente
 * 
 * Features:
 * - Botón "Auditar con IA"
 * - Compliance Score con gauge chart
 * - Referencias normativas (EASA, FAA, ICAO)
 * - Discrepancias detectadas
 * - Recommendations
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState } from 'react';
import { Brain, Play, CheckCircle, AlertTriangle, FileText, TrendingUp, Loader } from 'lucide-react';

const SeniorAuditorPanel = ({ evidence, onAnalysisComplete, analysis, language }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [territory, setTerritory] = useState('GLOBAL');

    // Territorios disponibles (Cielos Abiertos)
    const TERRITORIES = [
        { value: 'GLOBAL', label: '🌍 Global (Todas las Regulaciones)' },
        { value: 'AUSTRALIA', label: '🇦🇺 Australia (CASA)' },
        { value: 'BRAZIL', label: '🇧🇷 Brasil (ANAC)' },
        { value: 'CANADA', label: '🇨🇦 Canadá (TCCA)' },
        { value: 'CHILE', label: '🇨🇱 Chile (DGAC)' },
        { value: 'CHINA', label: '🇨🇳 China (CAAC)' },
        { value: 'COSTA_RICA', label: '🇨🇷 Costa Rica (DGAC)' },
        { value: 'ECUADOR', label: '🇪🇨 Ecuador (DGAC)' },
        { value: 'KENYA', label: '🇰🇪 Kenia (KCAA)' },
        { value: 'MALTA', label: '🇲🇹 Malta (TM CAD)' },
        { value: 'MEXICO', label: '🇲🇽 México (AFAC)' },
        { value: 'QATAR', label: '🇶🇦 Qatar (QCAA)' },
        { value: 'SOUTH_AFRICA', label: '🇿🇦 Sudáfrica (SACAA)' },
        { value: 'SWITZERLAND', label: '🇨🇭 Suiza (FOCA)' },
        { value: 'UK', label: '🇬🇧 Reino Unido (UK CAA)' }
    ];

    const handleAnalyze = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/v2/audit/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    evidence_id: evidence.id,
                    task_description: evidence.task_id || 'Visual inspection task',
                    territory: territory !== 'GLOBAL' ? territory : null,  // Filtro territorial
                    context: {
                        aircraft_type: 'Unknown', // TODO: Get from evidence
                        component: 'Component',
                        task_code: evidence.task_id,
                        has_supervisor_signature: false,
                        has_gps_evidence: !!evidence.metadata?.gps_latitude,
                        has_timestamp_valid: true,
                        has_photo_evidence: true
                    }
                })
            });

            const data = await response.json();

            if (data.success) {
                onAnalysisComplete?.(data);
            } else {
                throw new Error(data.detail || 'Analysis failed');
            }
        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            className="glass-card"
            style={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                background: 'var(--bg-card)',
                overflow: 'hidden'
            }}
        >
            {/* Header */}
            <div style={{
                padding: '20px',
                borderBottom: '1px solid var(--glass-border)'
            }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '16px'
                }}>
                    <Brain size={24} color="var(--primary)" />
                    <div>
                        <h3 style={{
                            fontSize: '16px',
                            fontWeight: 700,
                            color: 'var(--text-primary)',
                            marginBottom: '2px'
                        }}>
                            Coach Auditor Senior
                        </h3>
                        <p style={{
                            fontSize: '11px',
                            color: 'var(--text-muted)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px'
                        }}>
                            ANÁLISIS RAG MULTI-AGENTE
                        </p>
                    </div>
                </div>

                {/* Territory Selector */}
                {!analysis && (
                    <div style={{ marginBottom: '12px' }}>
                        <label style={{
                            display: 'block',
                            fontSize: '11px',
                            fontWeight: 600,
                            color: 'var(--text-muted)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            marginBottom: '8px'
                        }}>
                            Territorio / Jurisdicción
                        </label>
                        <select
                            value={territory}
                            onChange={(e) => setTerritory(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '10px 12px',
                                background: 'var(--bg-deep)',
                                border: '1px solid var(--glass-border)',
                                borderRadius: '8px',
                                color: 'var(--text-primary)',
                                fontSize: '13px',
                                fontWeight: 500,
                                cursor: 'pointer'
                            }}
                        >
                            {TERRITORIES.map(t => (
                                <option key={t.value} value={t.value}>
                                    {t.label}
                                </option>
                            ))}
                        </select>
                    </div>
                )}

                {/* Analyze Button */}
                {!analysis && (
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="btn"
                        style={{
                            width: '100%',
                            height: '44px',
                            background: 'var(--primary)',
                            color: 'white',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px'
                        }}
                    >
                        {loading ? (
                            <>
                                <Loader size={20} className="spin" />
                                Analizando...
                            </>
                        ) : (
                            <>
                                <Play size={20} />
                                Auditar con IA
                            </>
                        )}
                    </button>
                )}
            </div>

            {/* Content */}
            <div style={{
                flex: 1,
                overflow: 'auto',
                padding: '20px'
            }}>
                {error && (
                    <div style={{
                        padding: '16px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid var(--error)',
                        borderRadius: '8px',
                        color: 'var(--error)',
                        fontSize: '13px'
                    }}>
                        <AlertTriangle size={16} style={{ marginRight: '8px' }} />
                        {error}
                    </div>
                )}

                {!analysis && !error && !loading && (
                    <div style={{
                        textAlign: 'center',
                        padding: '40px 20px',
                        color: 'var(--text-secondary)',
                        fontSize: '13px'
                    }}>
                        <Brain size={48} color="var(--text-muted)" style={{ marginBottom: '16px', opacity: 0.5 }} />
                        <p>
                            Haz clic en "Auditar con IA" para analizar esta evidencia con el sistema RAG multi-agente
                        </p>
                    </div>
                )}

                {analysis && (
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '20px'
                    }}>
                        {/* Compliance Score */}
                        <div>
                            <div style={{
                                fontSize: '11px',
                                fontWeight: 600,
                                color: 'var(--text-muted)',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                marginBottom: '12px'
                            }}>
                                CUMPLIMIENTO NORMATIVO
                            </div>
                            <ComplianceGauge
                                score={analysis.compliance_score}
                                riskLevel={analysis.risk_level}
                            />
                        </div>

                        {/* Normative References */}
                        {analysis.normative_references && analysis.normative_references.length > 0 && (
                            <div>
                                <div style={{
                                    fontSize: '11px',
                                    fontWeight: 600,
                                    color: 'var(--text-muted)',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px',
                                    marginBottom: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px'
                                }}>
                                    <FileText size={12} />
                                    REFERENCIAS NORMATIVAS
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    {analysis.normative_references.slice(0, 5).map((ref, idx) => (
                                        <NormativeReference
                                            key={idx}
                                            reference={ref}
                                            language={language}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Discrepancies */}
                        {analysis.discrepancies && analysis.discrepancies.length > 0 && (
                            <div>
                                <div style={{
                                    fontSize: '11px',
                                    fontWeight: 600,
                                    color: 'var(--text-muted)',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px',
                                    marginBottom: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px'
                                }}>
                                    <AlertTriangle size={12} />
                                    DISCREPANCIAS DETECTADAS
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                    {analysis.discrepancies.map((disc, idx) => (
                                        <Discrepancy
                                            key={idx}
                                            discrepancy={disc}
                                            language={language}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* RAG Insights */}
                        {analysis.rag_insights && (
                            <div>
                                <div style={{
                                    fontSize: '11px',
                                    fontWeight: 600,
                                    color: 'var(--text-muted)',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px',
                                    marginBottom: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px'
                                }}>
                                    <TrendingUp size={12} />
                                    ANÁLISIS RAG
                                </div>
                                <div style={{
                                    padding: '12px',
                                    background: 'var(--bg-deep)',
                                    border: '1px solid var(--glass-border)',
                                    borderRadius: '8px',
                                    fontSize: '12px',
                                    color: 'var(--text-secondary)',
                                    lineHeight: '1.6'
                                }}>
                                    {analysis.rag_insights}
                                </div>
                            </div>
                        )}

                        {/* Processing Time */}
                        <div style={{
                            paddingTop: '16px',
                            borderTop: '1px solid var(--glass-border)',
                            fontSize: '10px',
                            color: 'var(--text-muted)',
                            textAlign: 'center'
                        }}>
                            Procesado en {analysis.processing_time_ms}ms
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Componente: Compliance Gauge
const ComplianceGauge = ({ score, riskLevel }) => {
    const getColor = () => {
        if (score >= 85) return 'var(--success)';
        if (score >= 60) return 'var(--warning)';
        return 'var(--error)';
    };

    return (
        <div style={{ textAlign: 'center' }}>
            {/* Score Circle */}
            <div style={{
                position: 'relative',
                width: '120px',
                height: '120px',
                margin: '0 auto 16px'
            }}>
                <svg width="120" height="120" style={{ transform: 'rotate(-90deg)' }}>
                    {/* Background circle */}
                    <circle
                        cx="60"
                        cy="60"
                        r="50"
                        fill="none"
                        stroke="var(--bg-deep)"
                        strokeWidth="12"
                    />
                    {/* Progress circle */}
                    <circle
                        cx="60"
                        cy="60"
                        r="50"
                        fill="none"
                        stroke={getColor()}
                        strokeWidth="12"
                        strokeDasharray={`${(score / 100) * 314} 314`}
                        strokeLinecap="round"
                    />
                </svg>
                {/* Score text */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    fontSize: '28px',
                    fontWeight: 700,
                    color: getColor()
                }}>
                    {score}%
                </div>
            </div>

            {/* Risk Badge */}
            <div style={{
                display: 'inline-flex',
                padding: '6px 16px',
                background: `${getColor()}15`,
                border: `1px solid ${getColor()}`,
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: 700,
                color: getColor(),
                textTransform: 'uppercase'
            }}>
                {riskLevel}
            </div>
        </div>
    );
};

// Componente: Normative Reference
const NormativeReference = ({ reference, language }) => (
    <div style={{
        padding: '12px',
        background: 'var(--bg-deep)',
        border: '1px solid var(--glass-border)',
        borderRadius: '8px',
        fontSize: '12px'
    }}>
        <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '6px'
        }}>
            <span style={{
                fontWeight: 700,
                color: 'var(--primary)'
            }}>
                {reference.authority}
            </span>
            <span style={{
                fontSize: '10px',
                padding: '2px 8px',
                background: `var(--primary)20`,
                borderRadius: '10px',
                color: 'var(--primary)'
            }}>
                {Math.round(reference.relevance * 100)}% relevancia
            </span>
        </div>
        <div style={{ color: 'var(--text-secondary)' }}>
            {reference.document}
            {reference.section && ` - ${reference.section}`}
        </div>
    </div>
);

// Componente: Discrepancy
const Discrepancy = ({ discrepancy, language }) => {
    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'critical':
            case 'high':
                return 'var(--error)';
            case 'medium':
                return 'var(--warning)';
            default:
                return 'var(--text-secondary)';
        }
    };

    return (
        <div style={{
            padding: '12px',
            background: `${getSeverityColor(discrepancy.severity)}10`,
            border: `1px solid ${getSeverityColor(discrepancy.severity)}`,
            borderRadius: '8px'
        }}>
            <div style={{
                fontSize: '10px',
                fontWeight: 700,
                color: getSeverityColor(discrepancy.severity),
                textTransform: 'uppercase',
                marginBottom: '6px'
            }}>
                {discrepancy.severity} - {discrepancy.regulation}
            </div>
            <div style={{
                fontSize: '12px',
                color: 'var(--text-primary)',
                marginBottom: '8px',
                lineHeight: '1.5'
            }}>
                {discrepancy.description}
            </div>
            {discrepancy.recommendation && (
                <div style={{
                    fontSize: '11px',
                    color: 'var(--text-secondary)',
                    fontStyle: 'italic',
                    display: 'flex',
                    gap: '6px'
                }}>
                    <CheckCircle size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{discrepancy.recommendation}</span>
                </div>
            )}
        </div>
    );
};

// CSS for spinner
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spin {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);

export default SeniorAuditorPanel;
