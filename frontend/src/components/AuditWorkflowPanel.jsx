/**
 * AuditWorkflowPanel.jsx
 * ======================
 * Panel principal de auditoría con:
 * - Formularios Zero-Entry (auto-completado)
 * - RCA Validator con feedback IA
 * - Sello Dorado Fail-Closed
 */

import { useState, useEffect } from 'react';
import {
    FileText, AlertTriangle, CheckCircle2, Lock, Unlock,
    RefreshCw, Send, AlertCircle, Sparkles, Award, Shield,
    ChevronDown, ChevronUp, Zap, Target
} from 'lucide-react';

const AuditWorkflowPanel = () => {
    // Audit Context State
    const [auditContext, setAuditContext] = useState(null);
    const [loading, setLoading] = useState(false);

    // Form States
    const [scopeForm, setScopeForm] = useState({
        audit_name: '',
        regulation: 'EASA',
        territory: 'GLOBAL',
        aircraft_type: '',
        location: '',
        component_serial: '',
        component_model: '',
        component_pn: ''
    });

    const [findingForm, setFindingForm] = useState({
        title: '',
        description: '',
        level: 2,
        component_serial: ''
    });

    const [rcaForm, setRcaForm] = useState({
        root_cause: '',
        corrective_action: '',
        responsible: '',
        target_date: ''
    });

    // RCA Validation State
    const [rcaValidation, setRcaValidation] = useState(null);
    const [validatingRca, setValidatingRca] = useState(false);

    // Sello Dorado State
    const [certifyStatus, setCertifyStatus] = useState(null);
    const [showCertifyTooltip, setShowCertifyTooltip] = useState(false);

    // Expanded Sections
    const [expandedSection, setExpandedSection] = useState('scope');

    // Generated Report State
    const [generatedReport, setGeneratedReport] = useState(null);

    // Fetch certification status
    const fetchCertifyStatus = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/v2/audit/can-certify');
            if (res.ok) {
                const data = await res.json();
                setCertifyStatus(data);
            }
        } catch (e) {
            console.error('Error fetching certify status:', e);
        }
    };

    useEffect(() => {
        fetchCertifyStatus();
        const interval = setInterval(fetchCertifyStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    // Create Audit Context
    const handleCreateContext = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/v2/audit/context', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    audit_name: scopeForm.audit_name,
                    regulation: scopeForm.regulation,
                    territory: scopeForm.territory,
                    aircraft_type: scopeForm.aircraft_type,
                    location: scopeForm.location,
                    components: scopeForm.component_serial ? [{
                        serial: scopeForm.component_serial,
                        model: scopeForm.component_model,
                        part_number: scopeForm.component_pn,
                        location: scopeForm.location
                    }] : []
                })
            });

            if (res.ok) {
                const data = await res.json();
                setAuditContext(data);
                setExpandedSection('finding');
                // Auto-fill finding component
                if (scopeForm.component_serial) {
                    setFindingForm(prev => ({ ...prev, component_serial: scopeForm.component_serial }));
                }
            }
        } catch (e) {
            console.error('Error creating context:', e);
        }
        setLoading(false);
    };

    // Create Finding with Inheritance
    const handleCreateFinding = async () => {
        if (!auditContext) return;
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/v2/audit/findings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    audit_id: auditContext.audit_id,
                    title: findingForm.title,
                    description: findingForm.description,
                    level: findingForm.level,
                    component_serial: findingForm.component_serial || null
                })
            });

            if (res.ok) {
                const data = await res.json();
                alert(`✅ Finding ${data.finding_id} creado con herencia automática!`);
                setExpandedSection('rca');
                fetchCertifyStatus();
            }
        } catch (e) {
            console.error('Error creating finding:', e);
        }
        setLoading(false);
    };

    // Validate RCA with AI
    const handleValidateRCA = async () => {
        setValidatingRca(true);
        setRcaValidation(null);
        try {
            const res = await fetch('http://localhost:8000/api/v2/audit/validate-rca', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    finding_id: 'F-DEMO',
                    rca_text: rcaForm.root_cause,
                    pac_text: rcaForm.corrective_action
                })
            });

            if (res.ok) {
                const data = await res.json();
                setRcaValidation(data);
            }
        } catch (e) {
            console.error('Error validating RCA:', e);
        }
        setValidatingRca(false);
    };

    // Section Header Component
    const SectionHeader = ({ title, icon: Icon, section, isComplete }) => (
        <div
            onClick={() => setExpandedSection(expandedSection === section ? null : section)}
            style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                background: expandedSection === section ? 'rgba(139, 92, 246, 0.15)' : 'rgba(0,0,0,0.2)',
                borderRadius: '8px',
                cursor: 'pointer',
                marginBottom: expandedSection === section ? '12px' : '0',
                border: `1px solid ${isComplete ? 'rgba(34, 197, 94, 0.4)' : 'rgba(139, 92, 246, 0.3)'}`
            }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Icon size={18} style={{ color: isComplete ? '#22c55e' : '#8b5cf6' }} />
                <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>{title}</span>
                {isComplete && <CheckCircle2 size={14} style={{ color: '#22c55e' }} />}
            </div>
            {expandedSection === section ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
    );

    return (
        <div className="glass-card" style={{ padding: '20px' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Target size={20} style={{ color: '#8b5cf6' }} />
                    <span style={{ fontSize: '14px', fontWeight: 600, letterSpacing: '1px' }}>
                        FLUJO DE AUDITORÍA
                    </span>
                </div>

                {/* Sello Dorado Button */}
                <div style={{ position: 'relative' }}>
                    <button
                        disabled={!certifyStatus?.can_certify}
                        onMouseEnter={() => setShowCertifyTooltip(true)}
                        onMouseLeave={() => setShowCertifyTooltip(false)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '10px 16px',
                            borderRadius: '8px',
                            border: 'none',
                            cursor: certifyStatus?.can_certify ? 'pointer' : 'not-allowed',
                            background: certifyStatus?.can_certify
                                ? 'linear-gradient(135deg, #fbbf24, #f59e0b)'
                                : 'rgba(100, 100, 100, 0.3)',
                            color: certifyStatus?.can_certify ? '#000' : '#888',
                            fontWeight: 600,
                            fontSize: '12px',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        {certifyStatus?.can_certify ? (
                            <>
                                <Unlock size={16} />
                                CERTIFICAR
                            </>
                        ) : (
                            <>
                                <Lock size={16} />
                                BLOQUEADO
                            </>
                        )}
                    </button>

                    {/* Tooltip for blocked certification */}
                    {showCertifyTooltip && !certifyStatus?.can_certify && certifyStatus?.blockers && (
                        <div style={{
                            position: 'absolute',
                            top: '100%',
                            right: 0,
                            marginTop: '8px',
                            width: '280px',
                            padding: '12px',
                            background: 'rgba(239, 68, 68, 0.95)',
                            borderRadius: '8px',
                            zIndex: 1000,
                            boxShadow: '0 4px 20px rgba(0,0,0,0.4)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                <AlertCircle size={16} />
                                <span style={{ fontWeight: 700, fontSize: '12px' }}>Certificación Denegada</span>
                            </div>
                            {certifyStatus.blockers.map((b, i) => (
                                <div key={i} style={{ fontSize: '11px', marginTop: '6px', opacity: 0.9 }}>
                                    <strong>{b.type}:</strong> {b.message}
                                    {b.findings && (
                                        <div style={{ fontSize: '10px', marginTop: '2px', opacity: 0.8 }}>
                                            IDs: {b.findings.join(', ')}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Section 1: Scope */}
            <SectionHeader title="1. SCOPE DE AUDITORÍA" icon={FileText} section="scope" isComplete={!!auditContext} />

            {expandedSection === 'scope' && (
                <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginBottom: '12px' }}>
                    {auditContext ? (
                        <div style={{ background: 'rgba(34, 197, 94, 0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                <Shield size={16} style={{ color: '#22c55e' }} />
                                <span style={{ fontWeight: 600, color: '#22c55e', fontSize: '12px' }}>CONTEXTO ACTIVO</span>
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                                <div><strong>ID:</strong> {auditContext.audit_id}</div>
                                <div><strong>Scope:</strong> {auditContext.scope?.aircraft_type} / {auditContext.scope?.regulation}</div>
                                <div><strong>Ubicación:</strong> {auditContext.scope?.location}</div>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                                <input
                                    placeholder="Nombre de Auditoría *"
                                    value={scopeForm.audit_name}
                                    onChange={e => setScopeForm({ ...scopeForm, audit_name: e.target.value })}
                                    style={inputStyle}
                                />
                                <select
                                    value={scopeForm.regulation}
                                    onChange={e => setScopeForm({ ...scopeForm, regulation: e.target.value })}
                                    style={inputStyle}
                                >
                                    <option value="EASA">EASA</option>
                                    <option value="FAA">FAA</option>
                                    <option value="ICAO">ICAO</option>
                                    <option value="CASA">CASA Australia</option>
                                    <option value="ISO">ISO</option>
                                </select>
                                <input
                                    placeholder="Tipo Aeronave (ej: B737-800)"
                                    value={scopeForm.aircraft_type}
                                    onChange={e => setScopeForm({ ...scopeForm, aircraft_type: e.target.value })}
                                    style={inputStyle}
                                />
                                <input
                                    placeholder="Ubicación (ej: Hangar 3)"
                                    value={scopeForm.location}
                                    onChange={e => setScopeForm({ ...scopeForm, location: e.target.value })}
                                    style={inputStyle}
                                />
                            </div>

                            <div style={{ marginBottom: '12px', padding: '10px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '6px' }}>
                                <div style={{ fontSize: '11px', color: '#8b5cf6', marginBottom: '8px', fontWeight: 600 }}>
                                    COMPONENTE (Opcional - se heredará automáticamente)
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
                                    <input
                                        placeholder="Serial Number"
                                        value={scopeForm.component_serial}
                                        onChange={e => setScopeForm({ ...scopeForm, component_serial: e.target.value })}
                                        style={inputStyle}
                                    />
                                    <input
                                        placeholder="Modelo"
                                        value={scopeForm.component_model}
                                        onChange={e => setScopeForm({ ...scopeForm, component_model: e.target.value })}
                                        style={inputStyle}
                                    />
                                    <input
                                        placeholder="Part Number"
                                        value={scopeForm.component_pn}
                                        onChange={e => setScopeForm({ ...scopeForm, component_pn: e.target.value })}
                                        style={inputStyle}
                                    />
                                </div>
                            </div>

                            <button onClick={handleCreateContext} disabled={loading || !scopeForm.audit_name} style={primaryButtonStyle}>
                                {loading ? <RefreshCw size={14} className="animate-spin" /> : <Zap size={14} />}
                                Crear Contexto de Auditoría
                            </button>
                        </>
                    )}
                </div>
            )}

            {/* Section 2: Finding */}
            <SectionHeader title="2. REGISTRAR HALLAZGO" icon={AlertTriangle} section="finding" isComplete={false} />

            {expandedSection === 'finding' && (
                <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginBottom: '12px' }}>
                    {!auditContext ? (
                        <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-tertiary)', fontSize: '12px' }}>
                            ⚠️ Primero debe crear el Scope de Auditoría
                        </div>
                    ) : (
                        <>
                            {/* Inherited Data Display (Read-only) */}
                            <div style={{
                                background: 'rgba(139, 92, 246, 0.1)',
                                padding: '10px',
                                borderRadius: '6px',
                                marginBottom: '12px',
                                border: '1px dashed rgba(139, 92, 246, 0.4)'
                            }}>
                                <div style={{ fontSize: '10px', color: '#8b5cf6', marginBottom: '4px', fontWeight: 600 }}>
                                    📋 DATOS HEREDADOS (Auto-completados)
                                </div>
                                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                                    Auditoría: {auditContext.scope?.audit_name} |
                                    Regulación: {auditContext.scope?.regulation} |
                                    Aeronave: {auditContext.scope?.aircraft_type || 'N/A'}
                                </div>
                            </div>

                            <input
                                placeholder="Título del Hallazgo *"
                                value={findingForm.title}
                                onChange={e => setFindingForm({ ...findingForm, title: e.target.value })}
                                style={{ ...inputStyle, marginBottom: '10px' }}
                            />
                            <textarea
                                placeholder="Descripción detallada..."
                                value={findingForm.description}
                                onChange={e => setFindingForm({ ...findingForm, description: e.target.value })}
                                style={{ ...inputStyle, height: '60px', resize: 'none', marginBottom: '10px' }}
                            />
                            <div style={{ display: 'flex', gap: '10px', marginBottom: '12px' }}>
                                <select
                                    value={findingForm.level}
                                    onChange={e => setFindingForm({ ...findingForm, level: parseInt(e.target.value) })}
                                    style={{ ...inputStyle, flex: 1 }}
                                >
                                    <option value={1}>🔴 Nivel 1 - Crítico/AOG</option>
                                    <option value={2}>🟠 Nivel 2 - Mayor</option>
                                    <option value={3}>🟡 Nivel 3 - Observación</option>
                                </select>
                                <input
                                    placeholder="Serial Component"
                                    value={findingForm.component_serial}
                                    onChange={e => setFindingForm({ ...findingForm, component_serial: e.target.value })}
                                    style={{ ...inputStyle, flex: 1, background: 'rgba(139, 92, 246, 0.2)' }}
                                    disabled={true}
                                />
                            </div>

                            <button onClick={handleCreateFinding} disabled={loading || !findingForm.title} style={primaryButtonStyle}>
                                {loading ? <RefreshCw size={14} className="animate-spin" /> : <Send size={14} />}
                                Crear Finding con Herencia
                            </button>
                        </>
                    )}
                </div>
            )}

            {/* Section 3: RCA with AI Validation */}
            <SectionHeader title="3. RCA + VALIDACIÓN IA" icon={Sparkles} section="rca" isComplete={false} />

            {expandedSection === 'rca' && (
                <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginBottom: '12px' }}>
                    <textarea
                        placeholder="Causa Raíz (Root Cause Analysis) *"
                        value={rcaForm.root_cause}
                        onChange={e => setRcaForm({ ...rcaForm, root_cause: e.target.value })}
                        style={{ ...inputStyle, height: '60px', resize: 'none', marginBottom: '10px' }}
                    />
                    <textarea
                        placeholder="Acción Correctiva (PAC) *"
                        value={rcaForm.corrective_action}
                        onChange={e => setRcaForm({ ...rcaForm, corrective_action: e.target.value })}
                        style={{ ...inputStyle, height: '60px', resize: 'none', marginBottom: '10px' }}
                    />

                    <button
                        onClick={handleValidateRCA}
                        disabled={validatingRca || !rcaForm.root_cause || !rcaForm.corrective_action}
                        style={{
                            ...primaryButtonStyle,
                            background: 'linear-gradient(135deg, #8b5cf6, #a78bfa)'
                        }}
                    >
                        {validatingRca ? <RefreshCw size={14} className="animate-spin" /> : <Sparkles size={14} />}
                        Validar con IA
                    </button>

                    {/* RCA Validation Feedback */}
                    {rcaValidation && (
                        <div style={{
                            marginTop: '12px',
                            padding: '12px',
                            borderRadius: '8px',
                            background: rcaValidation.is_acceptable
                                ? 'rgba(34, 197, 94, 0.15)'
                                : 'rgba(239, 68, 68, 0.15)',
                            border: `1px solid ${rcaValidation.is_acceptable ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`
                        }}>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                marginBottom: '8px'
                            }}>
                                {rcaValidation.is_acceptable ? (
                                    <CheckCircle2 size={18} style={{ color: '#22c55e' }} />
                                ) : (
                                    <AlertCircle size={18} style={{ color: '#ef4444' }} />
                                )}
                                <span style={{
                                    fontWeight: 700,
                                    fontSize: '13px',
                                    color: rcaValidation.is_acceptable ? '#22c55e' : '#ef4444'
                                }}>
                                    {rcaValidation.ai_recommendation}
                                </span>
                                <span style={{
                                    marginLeft: 'auto',
                                    padding: '2px 8px',
                                    borderRadius: '4px',
                                    fontSize: '11px',
                                    fontWeight: 700,
                                    background: rcaValidation.is_acceptable ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)',
                                    color: rcaValidation.is_acceptable ? '#22c55e' : '#ef4444'
                                }}>
                                    Score: {rcaValidation.quality_score}%
                                </span>
                            </div>

                            {rcaValidation.suggestions && rcaValidation.suggestions.length > 0 && (
                                <div style={{ marginTop: '8px' }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                                        💡 <strong>Sugerencias de mejora:</strong>
                                    </div>
                                    {rcaValidation.suggestions.map((s, i) => (
                                        <div key={i} style={{
                                            fontSize: '11px',
                                            color: 'var(--text-primary)',
                                            padding: '6px 10px',
                                            background: 'rgba(0,0,0,0.2)',
                                            borderRadius: '4px',
                                            marginTop: '4px'
                                        }}>
                                            {s}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Section 4: Generate AI Report */}
            <SectionHeader title="4. GENERAR INFORME IA" icon={Award} section="report" isComplete={false} />

            {expandedSection === 'report' && (
                <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginBottom: '12px' }}>
                    {!auditContext ? (
                        <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-tertiary)', fontSize: '12px' }}>
                            ⚠️ Primero debe crear el Scope de Auditoría
                        </div>
                    ) : (
                        <>
                            <div style={{
                                background: 'rgba(139, 92, 246, 0.1)',
                                padding: '12px',
                                borderRadius: '8px',
                                marginBottom: '12px',
                                border: '1px solid rgba(139, 92, 246, 0.3)'
                            }}>
                                <div style={{ fontSize: '11px', color: '#8b5cf6', marginBottom: '8px' }}>
                                    <strong>ℹ️ ¿Qué hace este botón?</strong>
                                </div>
                                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                                    La IA recopilará todos los hallazgos, RCAs y evidencias de esta auditoría
                                    y generará un borrador de informe técnico completo. El auditor podrá
                                    revisar y aprobar antes de emitir.
                                </div>
                            </div>

                            <button
                                onClick={async () => {
                                    setLoading(true);
                                    try {
                                        const res = await fetch(`http://localhost:8000/api/v2/audit/generate-report/${auditContext.audit_id}`);
                                        if (res.ok) {
                                            const data = await res.json();
                                            setGeneratedReport(data);
                                        }
                                    } catch (e) {
                                        console.error('Error generating report:', e);
                                    }
                                    setLoading(false);
                                }}
                                disabled={loading}
                                style={{
                                    ...primaryButtonStyle,
                                    background: 'linear-gradient(135deg, #f59e0b, #d97706)'
                                }}
                            >
                                {loading ? <RefreshCw size={14} className="animate-spin" /> : <Award size={14} />}
                                Generar Borrador de Informe
                            </button>

                            {/* Generated Report Display */}
                            {generatedReport && (
                                <div style={{
                                    marginTop: '16px',
                                    padding: '16px',
                                    background: 'rgba(0,0,0,0.3)',
                                    borderRadius: '8px',
                                    border: '1px solid rgba(139, 92, 246, 0.3)',
                                    maxHeight: '400px',
                                    overflowY: 'auto'
                                }}>
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        marginBottom: '12px'
                                    }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <CheckCircle2 size={16} style={{ color: '#22c55e' }} />
                                            <span style={{ fontWeight: 600, color: '#22c55e', fontSize: '12px' }}>
                                                BORRADOR GENERADO
                                            </span>
                                        </div>
                                        <span style={{
                                            fontSize: '10px',
                                            color: 'var(--text-tertiary)',
                                            background: 'rgba(0,0,0,0.3)',
                                            padding: '4px 8px',
                                            borderRadius: '4px'
                                        }}>
                                            {generatedReport.metadata?.findings_count || 0} findings
                                        </span>
                                    </div>

                                    <pre style={{
                                        fontSize: '11px',
                                        color: 'var(--text-secondary)',
                                        whiteSpace: 'pre-wrap',
                                        fontFamily: 'monospace',
                                        lineHeight: 1.5,
                                        margin: 0
                                    }}>
                                        {generatedReport.full_report}
                                    </pre>

                                    <div style={{
                                        marginTop: '12px',
                                        padding: '8px',
                                        background: 'rgba(139, 92, 246, 0.1)',
                                        borderRadius: '6px',
                                        fontSize: '10px',
                                        color: '#8b5cf6'
                                    }}>
                                        💡 {generatedReport.ai_note}
                                    </div>

                                    {/* Export PDF Button */}
                                    <button
                                        onClick={() => {
                                            window.open(`http://localhost:8000/api/v2/audit/export-pdf/${auditContext.audit_id}`, '_blank');
                                        }}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '8px',
                                            width: '100%',
                                            marginTop: '12px',
                                            padding: '12px',
                                            borderRadius: '8px',
                                            border: 'none',
                                            background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                                            color: '#fff',
                                            fontWeight: 600,
                                            fontSize: '12px',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        📄 Exportar PDF Profesional
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

// Styles
const inputStyle = {
    width: '100%',
    padding: '10px 12px',
    borderRadius: '6px',
    border: '1px solid rgba(255,255,255,0.1)',
    background: 'rgba(0,0,0,0.3)',
    color: 'var(--text-primary)',
    fontSize: '12px',
    outline: 'none'
};

const primaryButtonStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    width: '100%',
    padding: '12px',
    borderRadius: '8px',
    border: 'none',
    background: 'linear-gradient(135deg, #22c55e, #16a34a)',
    color: '#fff',
    fontWeight: 600,
    fontSize: '12px',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
};

export default AuditWorkflowPanel;
