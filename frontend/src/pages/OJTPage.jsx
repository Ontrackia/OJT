import React from 'react'
import {
    Users, UserCheck, Clock, Award, GraduationCap, Sparkles, CheckSquare, Plus, Eye
} from 'lucide-react'
import { useApp } from '../context/AppContext'
import { PageHeader, StatusBadge, ProgressBar } from '../components/common/SharedComponents'

export default function OJTPage() {
    const { t } = useApp()
    const trainees = [
        { id: 1, name: 'Carlos Rodríguez', role: 'B1 Technician', hours: 450, required: 600, comp: '8/12', level: 'intermediate' },
        { id: 2, name: 'María García', role: 'B2 Technician', hours: 580, required: 600, comp: '11/12', level: 'advanced' },
    ]
    return (
        <>
            <PageHeader title="OJT - On-the-Job Training" subtitle="Gestión de Formación Práctica" actions={<button className="btn btn-primary"><Plus size={18} />Nuevo Aprendiz</button>} />
            <div className="stats-grid" style={{ marginBottom: '24px' }}>
                <div className="stat-card"><div className="stat-icon primary"><Users size={24} /></div><div className="stat-content"><span className="stat-value">12</span><span className="stat-label">{t.trainees}</span></div></div>
                <div className="stat-card"><div className="stat-icon success"><UserCheck size={24} /></div><div className="stat-content"><span className="stat-value">5</span><span className="stat-label">{t.instructors}</span></div></div>
                <div className="stat-card"><div className="stat-icon warning"><Clock size={24} /></div><div className="stat-content"><span className="stat-value">2,450</span><span className="stat-label">{t.hoursCompleted}</span></div></div>
                <div className="stat-card"><div className="stat-icon primary"><Award size={24} /></div><div className="stat-content"><span className="stat-value">28</span><span className="stat-label">{t.certifications}</span></div></div>
            </div>
            <div className="dashboard-grid">
                <div className="card dashboard-grid-full">
                    <div className="card-header"><h3 className="card-title"><GraduationCap size={20} />{t.trainees}</h3></div>
                    <div className="table-container"><table className="data-table"><thead><tr><th>Nombre</th><th>Rol</th><th>Horas</th><th>Progreso</th><th>{t.competencies}</th><th>Nivel</th><th>{t.actions}</th></tr></thead>
                        <tbody>{trainees.map(tr => <tr key={tr.id}><td style={{ fontWeight: 600 }}>{tr.name}</td><td><span className="badge neutral">{tr.role}</span></td><td>{tr.hours}/{tr.required}h</td><td style={{ width: '120px' }}><ProgressBar value={Math.round(tr.hours / tr.required * 100)} /></td><td>{tr.comp}</td><td><StatusBadge status={tr.level} /></td><td><div style={{ display: 'flex', gap: '8px' }}><button className="icon-btn"><Eye size={16} /></button><button className="icon-btn"><Award size={16} /></button><button className="ai-assist-btn" style={{ padding: '6px 10px' }}><Sparkles size={14} /></button></div></td></tr>)}</tbody>
                    </table></div>
                </div>
                <div className="card"><div className="card-header"><h3 className="card-title"><Sparkles size={20} />Plan IA</h3></div><select className="form-select" style={{ marginBottom: '12px' }}>{trainees.map(tr => <option key={tr.id}>{tr.name}</option>)}</select><button className="ai-assist-btn" style={{ width: '100%', justifyContent: 'center', padding: '12px' }}><Sparkles size={18} />Generar Plan</button></div>
                <div className="card"><div className="card-header"><h3 className="card-title"><CheckSquare size={20} />{t.competencies}</h3></div>{['Engine Run-up', 'NDT Inspection', 'Component R&R'].map((c, i) => <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-tertiary)', borderRadius: '8px', marginBottom: '8px' }}><span>{c}</span><span className={`badge ${i < 2 ? 'success' : 'warning'}`}>{i < 2 ? 'Completado' : 'En Progreso'}</span></div>)}</div>
            </div>
        </>
    )
}
