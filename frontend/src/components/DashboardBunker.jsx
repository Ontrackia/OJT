/**
 * OnTrackIA OJT V2.0 - Panel de Control Operativo (Senior Auditor Mode)
 * ======================================================================
 * Professional Aviation Auditing Interface - Garmin/Collins Aerospace Style
 * 
 * Features:
 * - Territory/Jurisdiction Selection (16 Authorities)
 * - Evidence Analysis via RAG ("Cielos Abiertos")
 * - Compliance Score & Verdict Visualization
 * - SMS Risk Protocol Integration
 * 
 * @author OnTrackia Dev Team
 * @version 2.0.4
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';
import { FileText, AlertTriangle, ShieldCheck, Activity, UploadCloud, ChevronRight, Sun, Moon, Terminal, Server, Database, Award, Shield } from 'lucide-react';
import SyncIndicator from './SyncIndicator';
import SMSRadarPanel from './SMSRadarPanel';
import GlassCockpitPanel from './GlassCockpitPanel';
import AuditWorkflowPanel from './AuditWorkflowPanel';

const TERRITORIES = [
    { code: 'GLOBAL', name: 'Global Standard (ICAO)', flag: '🌍' },
    { code: 'EASA', name: 'EASA (Europe)', flag: '🇪🇺' },
    { code: 'FAA', name: 'FAA (USA)', flag: '🇺🇸' },
    { code: 'UK', name: 'UK CAA', flag: '🇬🇧' },
    { code: 'CANADA', name: 'TCCA (Canada)', flag: '🇨🇦' },
    { code: 'AUSTRALIA', name: 'CASA (Australia)', flag: '🇦🇺' },
    { code: 'BRAZIL', name: 'ANAC (Brasil)', flag: '🇧🇷' },
    { code: 'MEXICO', name: 'AFAC (México)', flag: '🇲🇽' },
    { code: 'URUGUAY', name: 'DINACIA (Uruguay)', flag: '🇺🇾' },
    { code: 'EL_SALVADOR', name: 'AAC (El Salvador)', flag: '🇸🇻' },
    { code: 'CHILE', name: 'DGAC (Chile)', flag: '🇨🇱' },
    { code: 'COLOMBIA', name: 'Aerocivil (Colombia)', flag: '🇨🇴' },
    { code: 'ECUADOR', name: 'DGAC (Ecuador)', flag: '🇪🇨' },
    { code: 'SWITZERLAND', name: 'FOCA (Switzerland)', flag: '🇨🇭' },
    { code: 'MALTA', name: 'TM CAD (Malta)', flag: '🇲🇹' },
    { code: 'QATAR', name: 'QCAA (Qatar)', flag: '🇶🇦' },
];

const ANALYSIS_STEPS = [
    "Inicializando protocolo de conexión segura...",
    "Cotejando base de datos regulatoria...",
    "Validando integridad forense de la evidencia...",
    "Generando dictamen de cumplimiento...",
    "Finalizando reporte técnico..."
];

const DashboardBunker = () => {
    const [territory, setTerritory] = useState(TERRITORIES[0]);
    const [evidenceText, setEvidenceText] = useState('');
    const [loading, setLoading] = useState(false);
    const [progressStep, setProgressStep] = useState(0);
    const [result, setResult] = useState(null);
    const [smsConfirmed, setSmsConfirmed] = useState(false);
    const [isDarkMode, setIsDarkMode] = useState(true);

    useEffect(() => {
        document.body.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    }, [isDarkMode]);

    const toggleTheme = () => setIsDarkMode(!isDarkMode);

    // Progressive Loading Simulation
    useEffect(() => {
        let interval;
        if (loading) {
            setProgressStep(0);
            interval = setInterval(() => {
                setProgressStep(prev => (prev < ANALYSIS_STEPS.length - 1 ? prev + 1 : prev));
            }, 800);
        }
        return () => clearInterval(interval);
    }, [loading]);

    const handleAudit = async () => {
        if (!evidenceText.trim()) return;

        setLoading(true);
        setResult(null);
        setSmsConfirmed(false);

        try {
            const response = await fetch('http://localhost:8000/api/v2/audit/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    evidence_id: `EVID-${Date.now()}`,
                    task_description: evidenceText,
                    territory: territory.code
                })
            });

            if (!response.ok) throw new Error('Error en auditoría');
            const data = await response.json();

            setTimeout(() => {
                setResult(data);
                setLoading(false);
            }, 1500);

        } catch (error) {
            console.error(error);
            alert("Error crítico de conectividad. Contacte a Soporte IT.");
            setLoading(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 90) return 'var(--success)';
        if (score >= 80) return 'var(--warning)';
        return 'var(--error)';
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'var(--bg-deep)',
            padding: '24px',
            fontFamily: 'var(--font-sans)',
            transition: 'background 0.3s ease',
            color: 'var(--text-primary)'
        }}>
            {/* Header Industrial */}
            <header style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '24px',
                padding: '16px 24px',
                background: 'var(--glass-bg)',
                borderBottom: '2px solid var(--primary)',
                borderRadius: 'var(--radius-sm)',
                boxShadow: 'var(--glass-shadow)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '4px',
                        background: 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}>
                        <ShieldCheck size={24} color="#ffffff" />
                    </div>
                    <div>
                        <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0, letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                            PANEL DE CONTROL OPERATIVO
                        </h1>
                        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', margin: 0, fontFamily: 'var(--font-mono)' }}>
                            SYS.VER.2.0.4 • SECURE CONNECTION
                        </p>
                    </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <button
                        onClick={toggleTheme}
                        style={{
                            width: '36px',
                            height: '36px',
                            background: 'transparent',
                            border: '1px solid var(--glass-border)',
                            borderRadius: '4px',
                            color: 'var(--text-secondary)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer'
                        }}
                    >
                        {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
                    </button>
                    <div style={{ height: '24px', width: '1px', background: 'var(--glass-border)' }}></div>
                    <SyncIndicator />
                </div>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(380px, 1fr) 1.5fr', gap: '16px' }}>

                {/* Left Panel: Input & Controls */}
                <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px', borderRadius: 'var(--radius-sm)' }}>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingBottom: '12px', borderBottom: '1px solid var(--glass-border)' }}>
                        <Terminal size={16} color="var(--primary)" />
                        <span style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Parámetros de Entrada</span>
                    </div>

                    {/* Territory Selector */}
                    <div>
                        <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '6px', fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>
                            Jurisdicción / Territorio
                        </label>
                        <div style={{ position: 'relative' }}>
                            <select
                                value={territory.code}
                                onChange={(e) => setTerritory(TERRITORIES.find(t => t.code === e.target.value))}
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    paddingLeft: '44px',
                                    background: 'var(--input-bg)',
                                    border: '1px solid var(--input-border)',
                                    borderRadius: 'var(--radius-sm)',
                                    color: 'var(--text-primary)',
                                    fontSize: '14px',
                                    fontFamily: 'var(--font-mono)',
                                    appearance: 'none',
                                    cursor: 'pointer'
                                }}
                            >
                                {TERRITORIES.map(t => (
                                    <option key={t.code} value={t.code}>
                                        {t.code} - {t.name}
                                    </option>
                                ))}
                            </select>
                            <span style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', fontSize: '18px' }}>
                                {territory.flag}
                            </span>
                            <ChevronRight style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-secondary)' }} size={16} />
                        </div>
                    </div>

                    {/* Evidence Input */}
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                        <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '6px', fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>
                            Evidencia Técnica (Log / Reporte)
                        </label>
                        <div style={{
                            flex: 1,
                            border: '1px solid var(--input-border)',
                            borderRadius: 'var(--radius-sm)',
                            background: 'var(--input-bg)',
                            display: 'flex',
                            flexDirection: 'column',
                            minHeight: '280px'
                        }}>
                            <textarea
                                placeholder="// Ingrese descripción técnica o pegue log de mantenimiento..."
                                value={evidenceText}
                                onChange={(e) => setEvidenceText(e.target.value)}
                                style={{
                                    width: '100%',
                                    flex: 1,
                                    padding: '16px',
                                    background: 'transparent',
                                    border: 'none',
                                    color: 'var(--text-primary)',
                                    fontSize: '13px',
                                    fontFamily: 'var(--font-mono)',
                                    lineHeight: '1.6',
                                    resize: 'none',
                                    outline: 'none'
                                }}
                            />
                            <div style={{
                                padding: '12px',
                                borderTop: '1px solid var(--glass-border)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '10px',
                                color: 'var(--text-secondary)',
                                fontSize: '12px'
                            }}>
                                <UploadCloud size={14} />
                                <span>Arrastrar archivos adjuntos (OCR Habilitado)</span>
                            </div>
                        </div>
                    </div>

                    {/* Industrial Action Button */}
                    <button
                        onClick={handleAudit}
                        disabled={loading || !evidenceText}
                        style={{
                            padding: '16px',
                            background: loading ? 'var(--input-border)' : 'var(--primary)',
                            border: 'none',
                            borderRadius: 'var(--radius-sm)',
                            color: '#ffffff',
                            fontSize: '13px',
                            fontWeight: 600,
                            letterSpacing: '1px',
                            textTransform: 'uppercase',
                            cursor: loading ? 'wait' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '10px',
                            opacity: (loading || !evidenceText) ? 0.7 : 1
                        }}
                    >
                        {loading ? (
                            <>
                                <Activity size={18} className="spin" />
                                PROCESANDO...
                            </>
                        ) : (
                            <>
                                <Database size={18} />
                                INICIAR ANÁLISIS FORENSE
                            </>
                        )}
                    </button>

                    {/* Progressive Loading Feedback */}
                    {loading && (
                        <div style={{ marginTop: '-10px' }}>
                            <div style={{ height: '4px', background: 'var(--input-bg)', borderRadius: '2px', overflow: 'hidden' }}>
                                <div style={{
                                    height: '100%',
                                    background: 'var(--info)',
                                    width: `${((progressStep + 1) / ANALYSIS_STEPS.length) * 100}%`,
                                    transition: 'width 0.5s ease'
                                }}></div>
                            </div>
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                marginTop: '6px',
                                fontSize: '10px',
                                color: 'var(--info)',
                                fontFamily: 'var(--font-mono)'
                            }}>
                                <span>STATUS_CODE: 10{progressStep}</span>
                                <span>{ANALYSIS_STEPS[progressStep]}</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Panel: Analysis Results */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

                    {!result && !loading && (
                        <div className="glass-card" style={{
                            flex: 1,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            textAlign: 'center',
                            opacity: 0.4,
                            borderStyle: 'dashed',
                            borderRadius: 'var(--radius-sm)'
                        }}>
                            <Server size={48} color="var(--text-secondary)" style={{ marginBottom: '16px' }} />
                            <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-primary)', marginBottom: '8px' }}>Sistema en Espera</h3>
                            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '250px' }}>
                                Esperando entrada de datos para iniciar correlación normativa.
                            </p>
                        </div>
                    )}

                    {result && (
                        <>
                            {/* Score & Verdict Card */}
                            <div className="glass-card" style={{ padding: '0', overflow: 'hidden', display: 'flex', borderRadius: 'var(--radius-sm)' }}>
                                <div style={{
                                    flex: '0 0 140px',
                                    padding: '24px',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    borderRight: '1px solid var(--glass-border)',
                                    background: 'rgba(0,0,0,0.1)'
                                }}>
                                    <div style={{ fontSize: '10px', color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', fontWeight: 600 }}>
                                        Compliance Idx
                                    </div>
                                    <div style={{ position: 'relative', width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                                            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--glass-border)" strokeWidth="3" />
                                            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke={getScoreColor(result.compliance_score)} strokeWidth="3" strokeDasharray={`${result.compliance_score}, 100`} />
                                        </svg>
                                        <span style={{ position: 'absolute', fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
                                            {result.compliance_score}
                                        </span>
                                    </div>
                                </div>

                                <div style={{
                                    flex: 1,
                                    padding: '24px',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    justifyContent: 'center',
                                    background: result.compliance_score >= 80
                                        ? 'linear-gradient(90deg, rgba(16, 185, 129, 0.05) 0%, transparent 100%)'
                                        : 'linear-gradient(90deg, rgba(239, 68, 68, 0.05) 0%, transparent 100%)'
                                }}>
                                    <h2 style={{
                                        fontSize: '24px',
                                        fontWeight: 800,
                                        color: result.compliance_score >= 80 ? 'var(--success)' : 'var(--error)',
                                        marginBottom: '4px',
                                        letterSpacing: '1px'
                                    }}>
                                        {result.compliance_score >= 80 ? 'DICTAMEN: APTO' : 'DICTAMEN: NO APTO'}
                                    </h2>
                                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                                        REF_ID: CA-{Date.now().toString().slice(-6)} • AUDITOR: AI_SENIOR_01
                                    </div>
                                </div>
                            </div>

                            {/* SMS Risk Module (Conditional) */}
                            {result.compliance_score < 80 && (
                                <div className="glass-card" style={{
                                    border: '1px solid var(--error)',
                                    background: 'rgba(239, 68, 68, 0.03)',
                                    borderRadius: 'var(--radius-sm)'
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px', color: 'var(--error)' }}>
                                        <AlertTriangle size={18} />
                                        <h3 style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase' }}>Incidencia Crítica Detectada</h3>
                                    </div>
                                    <div style={{
                                        background: 'var(--bg-deep)',
                                        padding: '12px',
                                        borderRadius: '4px',
                                        marginBottom: '12px',
                                        fontFamily: 'var(--font-mono)',
                                        fontSize: '11px',
                                        color: 'var(--text-primary)',
                                        borderLeft: '3px solid var(--error)'
                                    }}>
                                        <strong>PROTOCOLO SMS ACTIVADO:</strong><br />
                                        Nivel de Riesgo: ALTO<br />
                                        Acción Mandatoria: Detener operación y notificar a Quality Manager.
                                    </div>
                                    <button
                                        onClick={() => setSmsConfirmed(true)}
                                        disabled={smsConfirmed}
                                        style={{
                                            width: '100%',
                                            padding: '10px',
                                            background: smsConfirmed ? 'transparent' : 'var(--error)',
                                            border: smsConfirmed ? '1px solid var(--error)' : 'none',
                                            borderRadius: '4px',
                                            color: smsConfirmed ? 'var(--error)' : '#ffffff',
                                            fontWeight: 600,
                                            fontSize: '12px',
                                            cursor: smsConfirmed ? 'default' : 'pointer',
                                            textTransform: 'uppercase'
                                        }}
                                    >
                                        {smsConfirmed ? '✓ Incidencia Registrada en Sistema' : 'Confirmar Reporte de Seguridad'}
                                    </button>
                                </div>
                            )}

                            {/* RAG Analysis Detail */}
                            <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', borderRadius: 'var(--radius-sm)' }}>
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    marginBottom: '16px',
                                    borderBottom: '1px solid var(--glass-border)',
                                    paddingBottom: '12px'
                                }}>
                                    <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px', textTransform: 'uppercase' }}>
                                        <FileText size={16} color="var(--info)" />
                                        Informe Técnico ({territory.code})
                                    </h3>
                                    <div style={{ fontSize: '10px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                                        DOC.REF.AUTO_GEN
                                    </div>
                                </div>

                                <div style={{
                                    flex: 1,
                                    background: 'var(--bg-deep)',
                                    border: '1px solid var(--input-border)',
                                    borderRadius: '4px',
                                    padding: '16px',
                                    fontSize: '13px',
                                    fontFamily: 'var(--font-mono)',
                                    lineHeight: '1.5',
                                    color: 'var(--text-primary)',
                                    whiteSpace: 'pre-wrap',
                                    overflowY: 'auto',
                                    maxHeight: '400px'
                                }}>
                                    {result.mistral_analysis || "Análisis completado. Sin observaciones adicionales."}
                                </div>

                                <div style={{ marginTop: '12px', fontSize: '11px', color: 'var(--text-secondary)', display: 'flex', gap: '6px' }}>
                                    <span style={{ fontWeight: 600 }}>REFERENCIA NORMATIVA:</span>
                                    <span>{result.references?.[0]?.document || 'N/A'}</span>
                                </div>

                                {/* SELLO DORADO - Solo visible cuando APTO */}
                                {result.compliance_score >= 80 && (
                                    <button
                                        style={{
                                            marginTop: '20px',
                                            width: '100%',
                                            padding: '14px',
                                            background: 'linear-gradient(135deg, #eab308, #ca8a04)',
                                            border: 'none',
                                            borderRadius: '6px',
                                            color: '#000',
                                            fontSize: '14px',
                                            fontWeight: 700,
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '10px',
                                            textTransform: 'uppercase',
                                            boxShadow: '0 4px 12px rgba(234, 179, 8, 0.4)'
                                        }}
                                    >
                                        <Award size={20} />
                                        Aplicar Sello de Conformidad
                                    </button>
                                )}
                            </div>
                        </>
                    )}

                    {/* AUDIT WORKFLOW - Formularios Zero-Entry */}
                    <div style={{ marginTop: '24px' }}>
                        <AuditWorkflowPanel />
                    </div>

                    {/* GLASS COCKPIT - Vista de Pájaro */}
                    <div style={{ marginTop: '16px' }}>
                        <GlassCockpitPanel />
                    </div>

                    {/* SMS RADAR PANEL */}
                    <div style={{ marginTop: '16px' }}>
                        <SMSRadarPanel />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardBunker;
