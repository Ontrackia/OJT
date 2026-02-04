/**
 * OnTrackIA OJT V2.0 - Dashboard Senior Auditor Coach
 * ====================================================
 * Dashboard con AI scoring de reportes técnicos y detección de Dirty Dozen
 * 
 * Features:
 * - Score de Calidad (0-100) de reportes
 * - Visualización de Dirty Dozen detectadas
 * - Profundidad técnica vs superficialidad
 * - Alertas de compliance
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const SeniorAuditorDashboard = () => {
    const [reports, setReports] = useState([]);
    const [selectedReport, setSelectedReport] = useState(null);
    const [dirtyDozenStats, setDirtyDozenStats] = useState([]);

    // Dirty Dozen categories
    const DIRTY_DOZEN = [
        { id: 'fatigue', name: 'Fatiga', icon: '😴' },
        { id: 'complacency', name: 'Complacencia', icon: '😌' },
        { id: 'pressure', name: 'Presión', icon: '⏱️' },
        { id: 'distraction', name: 'Distracción', icon: '📱' },
        { id: 'lack_knowledge', name: 'Falta de Conocimiento', icon: '❓' },
        { id: 'teamwork', name: 'Trabajo en Equipo', icon: '👥' },
        { id: 'resources', name: 'Recursos', icon: '🔧' },
        { id: 'assertiveness', name: 'Asertividad', icon: '💪' },
        { id: 'stress', name: 'Estrés', icon: '😰' },
        { id: 'awareness', name: 'Conciencia Situacional', icon: '👁️' },
        { id: 'norms', name: 'Normas', icon: '📋' },
        { id: 'communication', name: 'Comunicación', icon: '💬' }
    ];

    useEffect(() => {
        // Simular carga de datos
        const mockReports = [
            {
                id: '1',
                technician: 'Juan Pérez',
                task_code: 'ATA-71-001',
                title: 'Inspección de turbina CFM56',
                quality_score: 85,
                depth_score: 8,
                word_count: 342,
                dirty_dozen: ['fatigue', 'teamwork', 'resources'],
                traceability: true,
                date: '2026-02-03'
            },
            {
                id: '2',
                technician: 'María González',
                task_code: 'ATA-32-015',
                title: 'Cambio de neumático tren principal',
                quality_score: 72,
                depth_score: 6,
                word_count: 189,
                dirty_dozen: ['pressure', 'resources'],
                traceability: true,
                date: '2026-02-02'
            },
            {
                id: '3',
                technician: 'Carlos Rodríguez',
                task_code: 'ATA-27-003',
                title: 'Calibración sistema fly-by-wire',
                quality_score: 92,
                depth_score: 9,
                word_count: 456,
                dirty_dozen: ['awareness', 'norms', 'communication'],
                traceability: true,
                date: '2026-02-01'
            }
        ];

        setReports(mockReports);

        // Calcular estadísticas de Dirty Dozen
        const stats = DIRTY_DOZEN.map(factor => {
            const count = mockReports.reduce((acc, report) => {
                return acc + (report.dirty_dozen.includes(factor.id) ? 1 : 0);
            }, 0);
            return {
                name: factor.name,
                count: count,
                icon: factor.icon
            };
        });

        setDirtyDozenStats(stats);
    }, []);

    const getScoreColor = (score) => {
        if (score >= 80) return 'high';
        if (score >= 60) return 'medium';
        return 'low';
    };

    const getScoreEmoji = (score) => {
        if (score >= 90) return '🏆';
        if (score >= 80) return '✅';
        if (score >= 70) return '👍';
        if (score >= 60) return '⚠️';
        return '❌';
    };

    return (
        <div style={{
            padding: '32px',
            maxWidth: '1400px',
            margin: '0 auto'
        }}>
            {/* Header */}
            <div style={{
                marginBottom: '32px',
                display: 'flex',
                alignItems: 'center',
                gap: '16px'
            }}>
                <div style={{ fontSize: '48px' }}>🤖</div>
                <div>
                    <h1 style={{
                        fontSize: '28px',
                        fontWeight: 700,
                        color: '#7c3aed',
                        marginBottom: '4px'
                    }}>
                        Senior Auditor Coach
                    </h1>
                    <p style={{
                        fontSize: '14px',
                        color: '#94a3b8'
                    }}>
                        AI-Powered Quality Assessment & Dirty Dozen Detection
                    </p>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-label">Reportes Analizados</div>
                    <div className="stat-value">{reports.length}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Score Promedio</div>
                    <div className="stat-value">
                        {Math.round(reports.reduce((acc, r) => acc + r.quality_score, 0) / reports.length || 0)}
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Profundidad Promedio</div>
                    <div className="stat-value">
                        {(reports.reduce((acc, r) => acc + r.depth_score, 0) / reports.length || 0).toFixed(1)}/10
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Factores Detectados</div>
                    <div className="stat-value">
                        {new Set(reports.flatMap(r => r.dirty_dozen)).size}
                    </div>
                </div>
            </div>

            {/* Reports Table */}
            <div className="glass-card" style={{ marginBottom: '32px' }}>
                <h2 style={{
                    fontSize: '20px',
                    fontWeight: 600,
                    marginBottom: '24px',
                    color: '#ffffff'
                }}>
                    📊 Reportes Recientes
                </h2>

                <table className="table">
                    <thead>
                        <tr>
                            <th>Técnico</th>
                            <th>Tarea</th>
                            <th>Título</th>
                            <th>Score</th>
                            <th>Profundidad</th>
                            <th>Palabras</th>
                            <th>Factores</th>
                            <th>Fecha</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reports.map(report => (
                            <tr key={report.id} onClick={() => setSelectedReport(report)} style={{ cursor: 'pointer' }}>
                                <td>{report.technician}</td>
                                <td>
                                    <code style={{
                                        background: 'rgba(124, 58, 237, 0.1)',
                                        padding: '4px 8px',
                                        borderRadius: '4px',
                                        fontSize: '12px',
                                        color: '#7c3aed'
                                    }}>
                                        {report.task_code}
                                    </code>
                                </td>
                                <td>{report.title}</td>
                                <td>
                                    <div className={`score-badge ${getScoreColor(report.quality_score)}`}>
                                        {getScoreEmoji(report.quality_score)} {report.quality_score}
                                    </div>
                                </td>
                                <td>
                                    <div style={{
                                        color: report.depth_score >= 7 ? 'var(--success)' : 'var(--warning)'
                                    }}>
                                        {report.depth_score}/10
                                    </div>
                                </td>
                                <td>{report.word_count}</td>
                                <td>
                                    <div style={{ display: 'flex', gap: '4px' }}>
                                        {report.dirty_dozen.slice(0, 3).map(factor => {
                                            const factorData = DIRTY_DOZEN.find(d => d.id === factor);
                                            return (
                                                <span key={factor} title={factorData?.name}>
                                                    {factorData?.icon}
                                                </span>
                                            );
                                        })}
                                        {report.dirty_dozen.length > 3 && (
                                            <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                                                +{report.dirty_dozen.length - 3}
                                            </span>
                                        )}
                                    </div>
                                </td>
                                <td>{report.date}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Dirty Dozen Chart */}
            <div className="glass-card">
                <h2 style={{
                    fontSize: '20px',
                    fontWeight: 600,
                    marginBottom: '24px',
                    color: '#ffffff'
                }}>
                    👥 Dirty Dozen - Factores Humanos Detectados
                </h2>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '16px'
                }}>
                    {dirtyDozenStats.filter(stat => stat.count > 0).map(stat => (
                        <div key={stat.name} style={{
                            background: 'rgba(124, 58, 237, 0.05)',
                            border: '1px solid rgba(124, 58, 237, 0.2)',
                            borderRadius: '8px',
                            padding: '16px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px'
                        }}>
                            <div style={{ fontSize: '32px' }}>{stat.icon}</div>
                            <div style={{ flex: 1 }}>
                                <div style={{
                                    fontSize: '14px',
                                    color: '#cbd5e1',
                                    marginBottom: '4px'
                                }}>
                                    {stat.name}
                                </div>
                                <div style={{
                                    fontSize: '24px',
                                    fontWeight: 700,
                                    color: '#7c3aed'
                                }}>
                                    {stat.count}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div style={{
                    marginTop: '32px',
                    padding: '16px',
                    background: 'rgba(245, 158, 11, 0.1)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                    borderRadius: '8px'
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        marginBottom: '8px'
                    }}>
                        <span style={{ fontSize: '24px' }}>💡</span>
                        <strong style={{ color: '#f59e0b' }}>Recomendación del Auditor Senior</strong>
                    </div>
                    <p style={{
                        fontSize: '14px',
                        color: '#cbd5e1',
                        lineHeight: 1.6,
                        margin: 0
                    }}>
                        Los factores más detectados son <strong>Fatiga</strong>, <strong>Trabajo en Equipo</strong> y <strong>Recursos</strong>.
                        Se recomienda implementar briefings pre-turno y verificar disponibilidad de herramientas especializadas.
                    </p>
                </div>
            </div>

            {/* Selected Report Detail */}
            {selectedReport && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0, 0, 0, 0.8)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    padding: '32px'
                }} onClick={() => setSelectedReport(null)}>
                    <div className="glass-card" style={{
                        maxWidth: '600px',
                        width: '100%'
                    }} onClick={(e) => e.stopPropagation()}>
                        <h3 style={{ marginBottom: '16px' }}>{selectedReport.title}</h3>
                        <div style={{ marginBottom: '24px' }}>
                            <div className={`score-badge ${getScoreColor(selectedReport.quality_score)}`} style={{
                                fontSize: '32px',
                                padding: '16px 24px'
                            }}>
                                {getScoreEmoji(selectedReport.quality_score)} {selectedReport.quality_score}/100
                            </div>
                        </div>
                        <div style={{ display: 'grid', gap: '12px' }}>
                            <div>
                                <strong>Profundidad Técnica:</strong> {selectedReport.depth_score}/10
                            </div>
                            <div>
                                <strong>Palabras:</strong> {selectedReport.word_count}
                            </div>
                            <div>
                                <strong>Trazabilidad:</strong> {selectedReport.traceability ? '✅ Sí' : '❌ No'}
                            </div>
                            <div>
                                <strong>Factores Dirty Dozen:</strong>
                                <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
                                    {selectedReport.dirty_dozen.map(factor => {
                                        const factorData = DIRTY_DOZEN.find(d => d.id === factor);
                                        return (
                                            <span key={factor} style={{
                                                background: 'rgba(124, 58, 237, 0.1)',
                                                padding: '4px 12px',
                                                borderRadius: '16px',
                                                fontSize: '14px'
                                            }}>
                                                {factorData?.icon} {factorData?.name}
                                            </span>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SeniorAuditorDashboard;
