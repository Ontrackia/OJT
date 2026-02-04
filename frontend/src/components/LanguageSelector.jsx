/**
 * OnTrackIA OJT V2.0 - Language Selector Component
 * =================================================
 * Selector de idioma ES/EN con soporte i18n
 * 
 * Idiomas soportados:
 * - Español (ES)
 * - English (EN)
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect, createContext, useContext } from 'react';
import { Globe } from 'lucide-react';

// Traducciones
const translations = {
    es: {
        // Dashboard
        'dashboard.title': 'Dashboard Búnker',
        'dashboard.subtitle': 'Trazabilidad Ultimate con Geolocalización Forense',
        'dashboard.active_technicians': 'Técnicos Activos',
        'dashboard.assigned_tasks': 'Tareas Asignadas',
        'dashboard.completed_tasks': 'Tareas Completadas',
        'dashboard.gps_evidences': 'Evidencias con GPS',
        'dashboard.quick_actions': 'Acciones Rápidas',
        'dashboard.progress': 'Progreso General',
        'dashboard.global_completeness': 'Completitud Global',
        'dashboard.total_hours': 'Horas Totales OJT',
        'dashboard.validation_rate': 'Tasa de Validación',
        'dashboard.certified_compliance': 'Compliance Certificado',

        // Actions
        'action.new_technician': 'Nuevo Técnico',
        'action.new_task': 'Nueva Tarea',
        'action.view_map': 'Ver Mapa',
        'action.validate': 'Validar',

        // Plans
        'plan.individual': 'Plan Individual',
        'plan.corporate': 'Plan Empresarial',
        'plan.threshold': 'Umbral de Cumplimiento',
        'plan.configure': 'Configurar Plan',

        // Senior Auditor
        'auditor.title': 'Senior Auditor Coach',
        'auditor.subtitle': 'Evaluación de Calidad con IA y Detección de Dirty Dozen',
        'auditor.reports_analyzed': 'Reportes Analizados',
        'auditor.average_score': 'Score Promedio',
        'auditor.average_depth': 'Profundidad Promedio',
        'auditor.factors_detected': 'Factores Detectados',
        'auditor.recent_reports': 'Reportes Recientes',
        'auditor.dirty_dozen': 'Dirty Dozen - Factores Humanos Detectados',
        'auditor.recommendation': 'Recomendación del Auditor Senior',

        // Sync
        'sync.online': 'En línea',
        'sync.offline': 'Sin conexión',
        'sync.syncing': 'Sincronizando...',

        // Theme
        'theme.day': 'Día',
        'theme.night': 'Noche',

        // General
        'general.loading': 'Cargando...',
        'general.error': 'Error',
        'general.success': 'Éxito',
        'general.cancel': 'Cancelar',
        'general.save': 'Guardar',
        'general.delete': 'Eliminar'
    },
    en: {
        // Dashboard
        'dashboard.title': 'Bunker Dashboard',
        'dashboard.subtitle': 'Ultimate Traceability with Forensic Geolocation',
        'dashboard.active_technicians': 'Active Technicians',
        'dashboard.assigned_tasks': 'Assigned Tasks',
        'dashboard.completed_tasks': 'Completed Tasks',
        'dashboard.gps_evidences': 'GPS Evidences',
        'dashboard.quick_actions': 'Quick Actions',
        'dashboard.progress': 'Overall Progress',
        'dashboard.global_completeness': 'Global Completeness',
        'dashboard.total_hours': 'Total OJT Hours',
        'dashboard.validation_rate': 'Validation Rate',
        'dashboard.certified_compliance': 'Certified Compliance',

        // Actions
        'action.new_technician': 'New Technician',
        'action.new_task': 'New Task',
        'action.view_map': 'View Map',
        'action.validate': 'Validate',

        // Plans
        'plan.individual': 'Individual Plan',
        'plan.corporate': 'Corporate Plan',
        'plan.threshold': 'Compliance Threshold',
        'plan.configure': 'Configure Plan',

        // Senior Auditor
        'auditor.title': 'Senior Auditor Coach',
        'auditor.subtitle': 'AI-Powered Quality Assessment & Dirty Dozen Detection',
        'auditor.reports_analyzed': 'Reports Analyzed',
        'auditor.average_score': 'Average Score',
        'auditor.average_depth': 'Average Depth',
        'auditor.factors_detected': 'Factors Detected',
        'auditor.recent_reports': 'Recent Reports',
        'auditor.dirty_dozen': 'Dirty Dozen - Human Factors Detected',
        'auditor.recommendation': 'Senior Auditor Recommendation',

        // Sync
        'sync.online': 'Online',
        'sync.offline': 'Offline',
        'sync.syncing': 'Syncing...',

        // Theme
        'theme.day': 'Day',
        'theme.night': 'Night',

        // General
        'general.loading': 'Loading...',
        'general.error': 'Error',
        'general.success': 'Success',
        'general.cancel': 'Cancel',
        'general.save': 'Save',
        'general.delete': 'Delete'
    }
};

// Context para i18n
const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
    const [language, setLanguage] = useState('es');

    useEffect(() => {
        // Cargar idioma guardado
        const savedLang = localStorage.getItem('ontrackia-language') || 'es';
        setLanguage(savedLang);
    }, []);

    const changeLanguage = (lang) => {
        setLanguage(lang);
        localStorage.setItem('ontrackia-language', lang);
    };

    const t = (key) => {
        return translations[language][key] || key;
    };

    return (
        <LanguageContext.Provider value={{ language, changeLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};

// Componente de selector
const LanguageSelector = () => {
    const { language, changeLanguage } = useLanguage();

    return (
        <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'var(--glass-bg)',
            backdropFilter: 'blur(10px)',
            border: '1px solid var(--glass-border)',
            borderRadius: '8px',
            padding: '8px 12px'
        }}>
            <Globe size={18} color="var(--text-secondary)" />
            <select
                value={language}
                onChange={(e) => changeLanguage(e.target.value)}
                style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-primary)',
                    fontSize: '14px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    outline: 'none'
                }}
            >
                <option value="es">ES</option>
                <option value="en">EN</option>
            </select>
        </div>
    );
};

export default LanguageSelector;
