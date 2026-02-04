/**
 * OnTrackIA OJT V2.0 - Plan Configuration Component
 * ==================================================
 * Componente para configurar plan Individual/Empresarial y threshold
 * 
 * Funcionalidad:
 * - Plan Individual: Usuario ajusta su propio threshold
 * - Plan Empresarial: Solo company_admin ajusta threshold
 * - Slider profesional estilo Clean Block
 * - Sin emojis, diseño aeronáutico
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';
import { Sliders, Lock, Unlock, Building, User } from 'lucide-react';
import { useLanguage } from './LanguageSelector';

const PlanConfigurationPanel = ({ userId, userRole, planType: initialPlanType }) => {
    const { t } = useLanguage();
    const [planType, setPlanType] = useState(initialPlanType || 'individual');
    const [threshold, setThreshold] = useState(70);
    const [canAdjustThreshold, setCanAdjustThreshold] = useState(false);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        // Determinar si el usuario puede ajustar el threshold
        if (planType === 'individual') {
            setCanAdjustThreshold(true);
        } else if (planType === 'corporate') {
            // Solo company_admin puede ajustar en plan empresarial
            setCanAdjustThreshold(userRole === 'company_admin');
        }
    }, [planType, userRole]);

    const handleThresholdChange = (e) => {
        setThreshold(parseInt(e.target.value));
    };

    const handleSave = async () => {
        setSaving(true);

        try {
            const response = await fetch(`/api/ojt/persons/${userId}/configure`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    plan_type: planType,
                    target_compliance_percentage: threshold
                })
            });

            if (response.ok) {
                alert(t('general.success'));
            } else {
                alert(t('general.error'));
            }
        } catch (error) {
            console.error('Error saving configuration:', error);
            alert(t('general.error'));
        } finally {
            setSaving(false);
        }
    };

    const getThresholdColor = () => {
        if (threshold >= 90) return '#10b981'; // Green
        if (threshold >= 70) return '#7c3aed'; // Purple
        if (threshold >= 50) return '#f59e0b'; // Orange
        return '#ef4444'; // Red
    };

    return (
        <div className="glass-card">
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '24px'
            }}>
                <Sliders size={24} color="var(--primary)" />
                <h2 style={{
                    fontSize: '20px',
                    fontWeight: 600,
                    color: 'var(--text-primary)'
                }}>
                    {t('plan.configure')}
                </h2>
            </div>

            {/* Plan Type Selector */}
            <div style={{ marginBottom: '32px' }}>
                <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: 500,
                    color: 'var(--text-secondary)',
                    marginBottom: '12px'
                }}>
                    Tipo de Plan
                </label>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '16px'
                }}>
                    {/* Individual Plan */}
                    <button
                        onClick={() => setPlanType('individual')}
                        className={`glass-card ${planType === 'individual' ? 'active' : ''}`}
                        style={{
                            padding: '20px',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            border: planType === 'individual'
                                ? '2px solid var(--primary)'
                                : '1px solid var(--glass-border)',
                            background: planType === 'individual'
                                ? 'rgba(124, 58, 237, 0.1)'
                                : 'var(--glass-bg)'
                        }}
                    >
                        <User size={32} color={planType === 'individual' ? 'var(--primary)' : 'var(--text-secondary)'} style={{ marginBottom: '12px' }} />
                        <div style={{
                            fontSize: '16px',
                            fontWeight: 600,
                            color: 'var(--text-primary)',
                            marginBottom: '8px'
                        }}>
                            {t('plan.individual')}
                        </div>
                        <div style={{
                            fontSize: '12px',
                            color: 'var(--text-secondary)',
                            lineHeight: 1.5
                        }}>
                            Control total sobre tu plan y umbral de cumplimiento
                        </div>
                    </button>

                    {/* Corporate Plan */}
                    <button
                        onClick={() => setPlanType('corporate')}
                        className={`glass-card ${planType === 'corporate' ? 'active' : ''}`}
                        style={{
                            padding: '20px',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            border: planType === 'corporate'
                                ? '2px solid var(--primary)'
                                : '1px solid var(--glass-border)',
                            background: planType === 'corporate'
                                ? 'rgba(124, 58, 237, 0.1)'
                                : 'var(--glass-bg)'
                        }}
                    >
                        <Building size={32} color={planType === 'corporate' ? 'var(--primary)' : 'var(--text-secondary)'} style={{ marginBottom: '12px' }} />
                        <div style={{
                            fontSize: '16px',
                            fontWeight: 600,
                            color: 'var(--text-primary)',
                            marginBottom: '8px'
                        }}>
                            {t('plan.corporate')}
                        </div>
                        <div style={{
                            fontSize: '12px',
                            color: 'var(--text-secondary)',
                            lineHeight: 1.5
                        }}>
                            Gestión centralizada por administrador de empresa
                        </div>
                    </button>
                </div>
            </div>

            {/* Threshold Slider */}
            <div style={{ marginBottom: '32px' }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '12px'
                }}>
                    <label style={{
                        fontSize: '14px',
                        fontWeight: 500,
                        color: 'var(--text-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}>
                        {canAdjustThreshold ? (
                            <><Unlock size={16} color="var(--success)" /> {t('plan.threshold')}</>
                        ) : (
                            <><Lock size={16} color="var(--error)" /> {t('plan.threshold')} (Bloqueado)</>
                        )}
                    </label>

                    <div style={{
                        fontSize: '32px',
                        fontWeight: 700,
                        color: getThresholdColor()
                    }}>
                        {threshold}%
                    </div>
                </div>

                {/* Slider profesional */}
                <div style={{ position: 'relative' }}>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        step="5"
                        value={threshold}
                        onChange={handleThresholdChange}
                        disabled={!canAdjustThreshold}
                        style={{
                            width: '100%',
                            height: '8px',
                            borderRadius: '4px',
                            background: `linear-gradient(to right, 
                ${getThresholdColor()} 0%, 
                ${getThresholdColor()} ${threshold}%, 
                var(--glass-bg) ${threshold}%, 
                var(--glass-bg) 100%)`,
                            outline: 'none',
                            transition: 'opacity 0.2s',
                            opacity: canAdjustThreshold ? 1 : 0.5,
                            cursor: canAdjustThreshold ? 'pointer' : 'not-allowed'
                        }}
                    />

                    {/* Marcadores de referencia */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginTop: '8px',
                        fontSize: '12px',
                        color: 'var(--text-muted)'
                    }}>
                        <span>0%</span>
                        <span>25%</span>
                        <span>50%</span>
                        <span>75%</span>
                        <span>100%</span>
                    </div>
                </div>

                {/* Mensaje de ayuda */}
                <div style={{
                    marginTop: '16px',
                    padding: '12px',
                    background: canAdjustThreshold
                        ? 'rgba(16, 185, 129, 0.05)'
                        : 'rgba(239, 68, 68, 0.05)',
                    border: `1px solid ${canAdjustThreshold ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.5
                }}>
                    {canAdjustThreshold ? (
                        <>
                            Umbral actual: <strong>{threshold}%</strong>. Este es el porcentaje mínimo de tareas
                            que debes completar para cerrar tu plan OJT.
                        </>
                    ) : (
                        <>
                            El umbral está bloqueado porque tu plan es <strong>Empresarial</strong>.
                            Solo el administrador de tu empresa puede modificar este valor.
                        </>
                    )}
                </div>
            </div>

            {/* Save Button */}
            <button
                onClick={handleSave}
                disabled={saving}
                className="btn"
                style={{
                    width: '100%',
                    opacity: saving ? 0.6 : 1
                }}
            >
                {saving ? t('general.loading') : t('general.save')}
            </button>
        </div>
    );
};

export default PlanConfigurationPanel;
