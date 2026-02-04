/**
 * OnTrackIA OJT V2.0 - Login Page + Emergency Report Button
 * ==========================================================
 * Página de autenticación con Protocolo Búnker
 * 
 * Features:
 * - Branding Deep Purple (#0a051a) + Glassmorphism
 * - Inputs/botones 44px (Ergonomía Aeronáutica)
 * - Rate limiting visual (5 intentos)
 * - JWT authentication
 * - PWA offline support
 * - Soporte ES/EN
 * - ⚠️ BOTÓN DE EMERGENCIA ANÓNIMO (SMS Integration)
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';
import { Lock, User, LogIn, AlertTriangle, Shield, X, Send, Upload, CheckCircle } from 'lucide-react';
import { useLanguage } from '../components/LanguageSelector';

const LoginPage = ({ onLoginSuccess }) => {
    const { t, language } = useLanguage();
    const [credentials, setCredentials] = useState({
        username: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [attemptCount, setAttemptCount] = useState(0);
    const [isBlocked, setIsBlocked] = useState(false);
    const [blockTimeRemaining, setBlockTimeRemaining] = useState(0);
    const [isOnline, setIsOnline] = useState(navigator.onLine);

    // Emergency Report Modal State
    const [showEmergencyModal, setShowEmergencyModal] = useState(false);
    const [emergencyReport, setEmergencyReport] = useState('');
    const [emergencyPhoto, setEmergencyPhoto] = useState(null);
    const [submittingEmergency, setSubmittingEmergency] = useState(false);
    const [emergencySuccess, setEmergencySuccess] = useState(null);

    useEffect(() => {
        // Detectar estado online/offline
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    useEffect(() => {
        // Countdown para desbloqueo
        if (blockTimeRemaining > 0) {
            const timer = setTimeout(() => {
                setBlockTimeRemaining(prev => prev - 1);
            }, 1000);

            if (blockTimeRemaining === 1) {
                setIsBlocked(false);
                setAttemptCount(0);
                setError('');
            }

            return () => clearTimeout(timer);
        }
    }, [blockTimeRemaining]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Verificar si está bloqueado
        if (isBlocked) {
            setError(
                language === 'es'
                    ? `Bloqueado temporalmente. Intenta en ${blockTimeRemaining}s`
                    : `Temporarily blocked. Try again in ${blockTimeRemaining}s`
            );
            return;
        }

        // Verificar conexión
        if (!isOnline) {
            setError(
                language === 'es'
                    ? 'Sin conexión. El login requiere conexión a Internet.'
                    : 'No connection. Login requires Internet connection.'
            );
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(credentials)
            });

            if (response.ok) {
                const data = await response.json();

                // Guardar token JWT
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));

                // Resetear intentos
                setAttemptCount(0);

                // Notificar éxito
                onLoginSuccess?.(data.user);

            } else {
                // Incrementar contador de intentos
                const newAttemptCount = attemptCount + 1;
                setAttemptCount(newAttemptCount);

                if (newAttemptCount >= 5) {
                    // Bloquear por 60 segundos
                    setIsBlocked(true);
                    setBlockTimeRemaining(60);
                    setError(
                        language === 'es'
                            ? 'Demasiados intentos fallidos. Bloqueado por 60 segundos.'
                            : 'Too many failed attempts. Blocked for 60 seconds.'
                    );
                } else {
                    const remainingAttempts = 5 - newAttemptCount;
                    setError(
                        language === 'es'
                            ? `Credenciales incorrectas. ${remainingAttempts} intentos restantes.`
                            : `Incorrect credentials. ${remainingAttempts} attempts remaining.`
                    );
                }
            }

        } catch (error) {
            console.error('Login error:', error);
            setError(
                language === 'es'
                    ? 'Error de conexión. Verifica tu red.'
                    : 'Connection error. Check your network.'
            );
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setCredentials(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // Handle Emergency Report Submission
    const handleEmergencySubmit = async () => {
        if (!emergencyReport.trim()) return;

        setSubmittingEmergency(true);

        try {
            // Convert photo to base64 if exists
            let photoBase64 = null;
            if (emergencyPhoto) {
                const reader = new FileReader();
                photoBase64 = await new Promise((resolve) => {
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(emergencyPhoto);
                });
            }

            const response = await fetch('http://localhost:8000/api/v2/sms/reports/voluntary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    description: emergencyReport,
                    photo_base64: photoBase64
                })
            });

            if (response.ok) {
                const data = await response.json();
                setEmergencySuccess(data);
                setEmergencyReport('');
                setEmergencyPhoto(null);

                // Auto-close after 5 seconds
                setTimeout(() => {
                    setShowEmergencyModal(false);
                    setEmergencySuccess(null);
                }, 5000);
            } else {
                throw new Error('Failed to submit report');
            }
        } catch (error) {
            console.error('Emergency report error:', error);
            alert(language === 'es'
                ? 'Error al enviar reporte. Intente más tarde.'
                : 'Error submitting report. Please try later.');
        } finally {
            setSubmittingEmergency(false);
        }
    };

    const handlePhotoChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setEmergencyPhoto(e.target.files[0]);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--bg-deep)',
            padding: '24px'
        }}>
            {/* Background Pattern */}
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                opacity: 0.03,
                backgroundImage: 'radial-gradient(circle at 25px 25px, var(--primary) 2%, transparent 0%), radial-gradient(circle at 75px 75px, var(--primary) 2%, transparent 0%)',
                backgroundSize: '100px 100px',
                pointerEvents: 'none'
            }} />

            {/* Login Card */}
            <div style={{
                width: '100%',
                maxWidth: '420px',
                position: 'relative',
                zIndex: 1
            }}>
                {/* Logo */}
                <div style={{
                    textAlign: 'center',
                    marginBottom: '32px'
                }}>
                    <div style={{
                        width: '80px',
                        height: '80px',
                        margin: '0 auto 16px',
                        borderRadius: '16px',
                        background: 'linear-gradient(135deg, var(--primary), var(--primary-hover))',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: '0 8px 24px rgba(124, 58, 237, 0.4)'
                    }}>
                        <Shield size={40} color="white" />
                    </div>

                    <h1 style={{
                        fontSize: '28px',
                        fontWeight: 700,
                        color: 'var(--text-primary)',
                        marginBottom: '8px'
                    }}>
                        OnTrackIA OJT
                    </h1>

                    <p style={{
                        fontSize: '14px',
                        color: 'var(--text-secondary)'
                    }}>
                        {language === 'es'
                            ? 'Protocolo Búnker - Acceso Seguro'
                            : 'Bunker Protocol - Secure Access'
                        }
                    </p>
                </div>

                {/* Form Card */}
                <form onSubmit={handleSubmit} className="glass-card">
                    {/* Offline Warning */}
                    {!isOnline && (
                        <div style={{
                            padding: '12px',
                            background: 'rgba(245, 158, 11, 0.1)',
                            border: '1px solid rgba(245, 158, 11, 0.3)',
                            borderRadius: '8px',
                            marginBottom: '24px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px'
                        }}>
                            <AlertTriangle size={20} color="#f59e0b" />
                            <span style={{ fontSize: '13px', color: '#f59e0b' }}>
                                {language === 'es'
                                    ? 'Modo sin conexión. El login requiere Internet.'
                                    : 'Offline mode. Login requires Internet.'
                                }
                            </span>
                        </div>
                    )}

                    {/* Error Message */}
                    {error && (
                        <div style={{
                            padding: '12px',
                            background: 'rgba(239, 68, 68, 0.1)',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            borderRadius: '8px',
                            marginBottom: '24px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px'
                        }}>
                            <AlertTriangle size={20} color="var(--error)" />
                            <span style={{ fontSize: '13px', color: 'var(--error)' }}>
                                {error}
                            </span>
                        </div>
                    )}

                    {/* Username Input */}
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{
                            display: 'block',
                            fontSize: '14px',
                            fontWeight: 500,
                            color: 'var(--text-secondary)',
                            marginBottom: '8px'
                        }}>
                            {language === 'es' ? 'Usuario' : 'Username'}
                        </label>

                        <div style={{ position: 'relative' }}>
                            <User
                                size={20}
                                color="var(--text-muted)"
                                style={{
                                    position: 'absolute',
                                    left: '14px',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    pointerEvents: 'none'
                                }}
                            />

                            <input
                                type="text"
                                name="username"
                                value={credentials.username}
                                onChange={handleInputChange}
                                disabled={loading || isBlocked}
                                placeholder={language === 'es' ? 'Ingresa tu usuario' : 'Enter your username'}
                                required
                                style={{
                                    width: '100%',
                                    height: '44px',
                                    paddingLeft: '44px',
                                    paddingRight: '14px',
                                    background: 'var(--bg-deep)',
                                    border: '1px solid var(--glass-border)',
                                    borderRadius: '8px',
                                    color: 'var(--text-primary)',
                                    fontSize: '14px',
                                    outline: 'none',
                                    transition: 'border-color 0.2s'
                                }}
                                onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                                onBlur={(e) => e.target.style.borderColor = 'var(--glass-border)'}
                            />
                        </div>
                    </div>

                    {/* Password Input */}
                    <div style={{ marginBottom: '24px' }}>
                        <label style={{
                            display: 'block',
                            fontSize: '14px',
                            fontWeight: 500,
                            color: 'var(--text-secondary)',
                            marginBottom: '8px'
                        }}>
                            {language === 'es' ? 'Contraseña' : 'Password'}
                        </label>

                        <div style={{ position: 'relative' }}>
                            <Lock
                                size={20}
                                color="var(--text-muted)"
                                style={{
                                    position: 'absolute',
                                    left: '14px',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    pointerEvents: 'none'
                                }}
                            />

                            <input
                                type="password"
                                name="password"
                                value={credentials.password}
                                onChange={handleInputChange}
                                disabled={loading || isBlocked}
                                placeholder={language === 'es' ? 'Ingresa tu contraseña' : 'Enter your password'}
                                required
                                style={{
                                    width: '100%',
                                    height: '44px',
                                    paddingLeft: '44px',
                                    paddingRight: '14px',
                                    background: 'var(--bg-deep)',
                                    border: '1px solid var(--glass-border)',
                                    borderRadius: '8px',
                                    color: 'var(--text-primary)',
                                    fontSize: '14px',
                                    outline: 'none',
                                    transition: 'border-color 0.2s'
                                }}
                                onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                                onBlur={(e) => e.target.style.borderColor = 'var(--glass-border)'}
                            />
                        </div>
                    </div>

                    {/* Login Button */}
                    <button
                        type="submit"
                        disabled={loading || isBlocked || !isOnline}
                        className="btn"
                        style={{
                            width: '100%',
                            height: '44px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            fontSize: '16px',
                            fontWeight: 600,
                            opacity: (loading || isBlocked || !isOnline) ? 0.5 : 1
                        }}
                    >
                        {loading ? (
                            <span>{language === 'es' ? 'Verificando...' : 'Verifying...'}</span>
                        ) : (
                            <>
                                <LogIn size={20} />
                                <span>{language === 'es' ? 'Iniciar Sesión' : 'Log In'}</span>
                            </>
                        )}
                    </button>

                    {/* Attempt Counter */}
                    {attemptCount > 0 && !isBlocked && (
                        <div style={{
                            marginTop: '16px',
                            textAlign: 'center',
                            fontSize: '12px',
                            color: 'var(--warning)'
                        }}>
                            {language === 'es'
                                ? `${attemptCount}/5 intentos utilizados`
                                : `${attemptCount}/5 attempts used`
                            }
                        </div>
                    )}
                </form>

                {/* ==================== EMERGENCY BUTTON ==================== */}
                <button
                    onClick={() => setShowEmergencyModal(true)}
                    style={{
                        width: '100%',
                        marginTop: '20px',
                        padding: '14px 20px',
                        background: 'rgba(245, 158, 11, 0.1)',
                        border: '1px solid rgba(245, 158, 11, 0.3)',
                        borderRadius: '8px',
                        color: '#f59e0b',
                        fontSize: '14px',
                        fontWeight: 500,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '10px',
                        transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(245, 158, 11, 0.2)';
                        e.target.style.borderColor = '#f59e0b';
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(245, 158, 11, 0.1)';
                        e.target.style.borderColor = 'rgba(245, 158, 11, 0.3)';
                    }}
                >
                    <AlertTriangle size={18} />
                    {language === 'es'
                        ? '⚠️ Reporte Voluntario de Seguridad (Anónimo)'
                        : '⚠️ Voluntary Safety Report (Anonymous)'}
                </button>

                {/* Footer */}
                <div style={{
                    marginTop: '24px',
                    textAlign: 'center',
                    fontSize: '12px',
                    color: 'var(--text-muted)'
                }}>
                    {language === 'es'
                        ? 'Sistema protegido con autenticación JWT y rate limiting'
                        : 'System protected with JWT authentication and rate limiting'
                    }
                </div>
            </div>

            {/* ==================== EMERGENCY MODAL ==================== */}
            {showEmergencyModal && (
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
                    padding: '24px'
                }}>
                    <div className="glass-card" style={{
                        width: '100%',
                        maxWidth: '500px',
                        position: 'relative'
                    }}>
                        {/* Modal Header */}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '20px',
                            paddingBottom: '16px',
                            borderBottom: '1px solid var(--glass-border)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <AlertTriangle size={24} color="#f59e0b" />
                                <h2 style={{
                                    fontSize: '18px',
                                    fontWeight: 700,
                                    color: 'var(--text-primary)',
                                    margin: 0
                                }}>
                                    {language === 'es'
                                        ? 'Reporte de Seguridad Anónimo'
                                        : 'Anonymous Safety Report'}
                                </h2>
                            </div>
                            <button
                                onClick={() => {
                                    setShowEmergencyModal(false);
                                    setEmergencySuccess(null);
                                }}
                                style={{
                                    background: 'transparent',
                                    border: 'none',
                                    color: 'var(--text-muted)',
                                    cursor: 'pointer',
                                    padding: '4px'
                                }}
                            >
                                <X size={24} />
                            </button>
                        </div>

                        {emergencySuccess ? (
                            /* Success State */
                            <div style={{ textAlign: 'center', padding: '20px 0' }}>
                                <CheckCircle size={64} color="#10b981" style={{ marginBottom: '16px' }} />
                                <h3 style={{
                                    color: '#10b981',
                                    fontSize: '18px',
                                    marginBottom: '12px'
                                }}>
                                    {language === 'es'
                                        ? '¡Reporte Enviado!'
                                        : 'Report Submitted!'}
                                </h3>
                                <p style={{
                                    color: 'var(--text-secondary)',
                                    fontSize: '14px',
                                    marginBottom: '16px'
                                }}>
                                    {language === 'es'
                                        ? 'Su reporte será procesado de forma confidencial.'
                                        : 'Your report will be processed confidentially.'}
                                </p>
                                <div style={{
                                    background: 'var(--bg-deep)',
                                    padding: '12px',
                                    borderRadius: '8px',
                                    fontFamily: 'var(--font-mono)',
                                    fontSize: '12px',
                                    color: 'var(--text-muted)'
                                }}>
                                    <div>ID: {emergencySuccess.report_id}</div>
                                    <div>SHA-256: {emergencySuccess.sha256_proof}</div>
                                </div>
                            </div>
                        ) : (
                            /* Form State */
                            <>
                                <p style={{
                                    fontSize: '13px',
                                    color: 'var(--text-secondary)',
                                    marginBottom: '20px',
                                    lineHeight: 1.5
                                }}>
                                    {language === 'es'
                                        ? 'Describe el riesgo o incidente observado. Tu identidad permanecerá anónima. El sistema registrará timestamp y SHA-256 para trazabilidad forense.'
                                        : 'Describe the observed risk or incident. Your identity will remain anonymous. The system will record timestamp and SHA-256 for forensic traceability.'}
                                </p>

                                <textarea
                                    value={emergencyReport}
                                    onChange={(e) => setEmergencyReport(e.target.value)}
                                    placeholder={language === 'es'
                                        ? 'Describa el riesgo de seguridad observado...'
                                        : 'Describe the observed safety risk...'}
                                    style={{
                                        width: '100%',
                                        minHeight: '120px',
                                        padding: '14px',
                                        background: 'var(--bg-deep)',
                                        border: '1px solid var(--glass-border)',
                                        borderRadius: '8px',
                                        color: 'var(--text-primary)',
                                        fontSize: '14px',
                                        resize: 'vertical',
                                        outline: 'none',
                                        marginBottom: '16px'
                                    }}
                                />

                                {/* Photo Upload */}
                                <div style={{ marginBottom: '20px' }}>
                                    <label style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '10px',
                                        padding: '12px 16px',
                                        background: 'var(--bg-deep)',
                                        border: '1px dashed var(--glass-border)',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        color: 'var(--text-secondary)',
                                        fontSize: '13px'
                                    }}>
                                        <Upload size={18} />
                                        {emergencyPhoto
                                            ? emergencyPhoto.name
                                            : (language === 'es' ? 'Adjuntar foto (opcional)' : 'Attach photo (optional)')}
                                        <input
                                            type="file"
                                            accept="image/*"
                                            onChange={handlePhotoChange}
                                            style={{ display: 'none' }}
                                        />
                                    </label>
                                </div>

                                {/* Submit Button */}
                                <button
                                    onClick={handleEmergencySubmit}
                                    disabled={!emergencyReport.trim() || submittingEmergency}
                                    style={{
                                        width: '100%',
                                        padding: '14px',
                                        background: submittingEmergency ? 'var(--input-border)' : '#f59e0b',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: '#000',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        cursor: submittingEmergency ? 'wait' : 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '8px',
                                        opacity: !emergencyReport.trim() ? 0.5 : 1
                                    }}
                                >
                                    {submittingEmergency ? (
                                        <>Enviando...</>
                                    ) : (
                                        <>
                                            <Send size={18} />
                                            {language === 'es' ? 'Enviar Reporte Anónimo' : 'Submit Anonymous Report'}
                                        </>
                                    )}
                                </button>

                                {/* Forensic Notice */}
                                <div style={{
                                    marginTop: '16px',
                                    padding: '10px',
                                    background: 'rgba(59, 130, 246, 0.1)',
                                    borderRadius: '6px',
                                    fontSize: '11px',
                                    color: 'var(--info)',
                                    fontFamily: 'var(--font-mono)'
                                }}>
                                    🔒 SHA-256 • ICAO SMS • Trazabilidad Forense
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default LoginPage;

