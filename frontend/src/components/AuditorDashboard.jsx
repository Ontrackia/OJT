/**
 * OnTrackIA OJT V2.0 - Auditor Dashboard (Professional Light Theme)
 * ==================================================================
 * Dashboard profesional con sidebar y tema claro
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';
import { Search, Filter, AlertTriangle, CheckCircle, AlertCircle, Brain, Eye, FileText, TrendingUp } from 'lucide-react';
import '../styles/professional-theme.css';
import EvidenceGrid from './EvidenceGrid';
import ForensicLightbox from './ForensicLightbox';
import SeniorAuditorPanel from './SeniorAuditorPanel';

const AuditorDashboard = () => {
    const [evidences, setEvidences] = useState([]);
    const [selectedEvidence, setSelectedEvidence] = useState(null);
    const [riskFilter, setRiskFilter] = useState('all');
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState(null);
    const [lightboxOpen, setLightboxOpen] = useState(false);
    const [aiAnalysis, setAiAnalysis] = useState(null);

    useEffect(() => {
        fetchEvidences();
        fetchStats();
    }, [riskFilter]);

    const fetchEvidences = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (riskFilter !== 'all') {
                params.append('risk_level', riskFilter);
            }

            const response = await fetch(`/api/v2/audit/evidences?${params}`);
            const data = await response.json();

            if (data.success) {
                setEvidences(data.evidences || []);
            }
        } catch (error) {
            console.error('Error fetching evidences:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await fetch('/api/v2/audit/stats');
            const data = await response.json();

            if (data.success) {
                setStats(data);
            }
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    };

    const handleEvidenceSelect = (evidence) => {
        setSelectedEvidence(evidence);
        setLightboxOpen(true);
        setAiAnalysis(null);
    };

    const handleCloseLightbox = () => {
        setLightboxOpen(false);
        setSelectedEvidence(null);
        setAiAnalysis(null);
    };

    const handleAiAnalysis = async (analysisResult) => {
        setAiAnalysis(analysisResult);
        await fetchEvidences();
    };

    return (
        <div className="app-container">
            {/* Sidebar */}
            <div className="sidebar">
                <div className="sidebar-header">
                    <div className="sidebar-logo">OnTrackIA</div>
                    <div className="sidebar-subtitle">Sistema OJT V2.0</div>
                </div>

                <nav className="sidebar-nav">
                    <div className="sidebar-nav-item">
                        <Eye size={18} />
                        Dashboard
                    </div>
                    <div className="sidebar-nav-item active">
                        <Brain size={18} />
                        Auditor Dashboard
                    </div>
                    <div className="sidebar-nav-item">
                        <FileText size={18} />
                        Visual Scans
                    </div>
                    <div className="sidebar-nav-item">
                        <TrendingUp size={18} />
                        Reports
                    </div>
                </nav>
            </div>

            {/* Main Content */}
            <div className="main-content">
                {/* Header */}
                <div style={{ marginBottom: '32px' }}>
                    <h1 style={{
                        fontSize: '28px',
                        fontWeight: 700,
                        color: 'var(--text-primary)',
                        marginBottom: '8px'
                    }}>
                        Dashboard Auditor V2.0
                    </h1>
                    <p style={{
                        fontSize: '14px',
                        color: 'var(--text-secondary)',
                        marginBottom: '24px'
                    }}>
                        Gestión y análisis de auditorías con IA multi-agente
                    </p>

                    {/* Stats Cards */}
                    {stats && (
                        <div className="grid grid-cols-4" style={{ marginTop: '24px' }}>
                            <div className="stat-card">
                                <div className="stat-value" style={{ color: 'var(--primary)' }}>
                                    {stats.total_evidences}
                                </div>
                                <div className="stat-label">Evidencias Totales</div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-value" style={{ color: 'var(--danger)' }}>
                                    {stats.risk_distribution?.red || 0}
                                </div>
                                <div className="stat-label">
                                    <AlertTriangle size={14} style={{ display: 'inline', marginRight: '4px' }} />
                                    Riesgo Alto
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-value" style={{ color: 'var(--warning)' }}>
                                    {stats.risk_distribution?.yellow || 0}
                                </div>
                                <div className="stat-label">
                                    <AlertCircle size={14} style={{ display: 'inline', marginRight: '4px' }} />
                                    Riesgo Medio
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-value" style={{ color: 'var(--success)' }}>
                                    {stats.risk_distribution?.green || 0}
                                </div>
                                <div className="stat-label">
                                    <CheckCircle size={14} style={{ display: 'inline', marginRight: '4px' }} />
                                    Cumplimiento OK
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Filters */}
                <div className="card" style={{ marginBottom: '24px' }}>
                    <div className="card-body">
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '16px',
                            flexWrap: 'wrap'
                        }}>
                            <Filter size={20} color="var(--text-secondary)" />
                            <span style={{
                                fontSize: '14px',
                                fontWeight: 600,
                                color: 'var(--text-primary)'
                            }}>
                                Filtrar por Nivel de Riesgo:
                            </span>

                            <div style={{ display: 'flex', gap: '8px', flex: 1 }}>
                                <button
                                    onClick={() => setRiskFilter('all')}
                                    className={riskFilter === 'all' ? 'btn btn-primary btn-sm' : 'btn btn-outline btn-sm'}
                                >
                                    Todos ({stats?.total_evidences || 0})
                                </button>
                                <button
                                    onClick={() => setRiskFilter('red')}
                                    className={riskFilter === 'red' ? 'btn btn-sm' : 'btn btn-outline btn-sm'}
                                    style={riskFilter === 'red' ? { background: 'var(--danger)', color: 'white' } : {}}
                                >
                                    Rojo ({stats?.risk_distribution?.red || 0})
                                </button>
                                <button
                                    onClick={() => setRiskFilter('yellow')}
                                    className={riskFilter === 'yellow' ? 'btn btn-sm' : 'btn btn-outline btn-sm'}
                                    style={riskFilter === 'yellow' ? { background: 'var(--warning)', color: 'white' } : {}}
                                >
                                    Amarillo ({stats?.risk_distribution?.yellow || 0})
                                </button>
                                <button
                                    onClick={() => setRiskFilter('green')}
                                    className={riskFilter === 'green' ? 'btn btn-sm' : 'btn btn-outline btn-sm'}
                                    style={riskFilter === 'green' ? { background: 'var(--success)', color: 'white' } : {}}
                                >
                                    Verde ({stats?.risk_distribution?.green || 0})
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Evidence Grid */}
                {loading ? (
                    <div style={{
                        textAlign: 'center',
                        padding: '80px',
                        color: 'var(--text-secondary)'
                    }}>
                        <div className="spinner" style={{ margin: '0 auto' }}></div>
                        <p style={{ marginTop: '16px' }}>Cargando evidencias...</p>
                    </div>
                ) : evidences.length === 0 ? (
                    <div className="card">
                        <div className="card-body" style={{ textAlign: 'center', padding: '80px' }}>
                            <Search size={48} color="var(--text-muted)" style={{ marginBottom: '16px' }} />
                            <p style={{ color: 'var(--text-secondary)' }}>
                                No se encontraron evidencias con los filtros seleccionados
                            </p>
                        </div>
                    </div>
                ) : (
                    <EvidenceGrid
                        evidences={evidences}
                        onEvidenceSelect={handleEvidenceSelect}
                    />
                )}

                {/* Forensic Lightbox */}
                {lightboxOpen && selectedEvidence && (
                    <ForensicLightbox
                        evidence={selectedEvidence}
                        onClose={handleCloseLightbox}
                        renderSidePanel={() => (
                            <SeniorAuditorPanel
                                evidence={selectedEvidence}
                                onAnalysisComplete={handleAiAnalysis}
                                analysis={aiAnalysis}
                            />
                        )}
                    />
                )}
            </div>
        </div>
    );
};

export default AuditorDashboard;
