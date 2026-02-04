import React, { useState } from 'react';
import { LogIn, AlertTriangle, Shield } from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';
import SMSQuickReport from '../components/SMSQuickReport';

const Login: React.FC = () => {
    const [language, setLanguage] = useState<'es' | 'en'>('es');
    const [showSMSReport, setShowSMSReport] = useState(false);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });

    const translations = {
        es: {
            title: 'OnTrackIA V1-Core',
            subtitle: 'Sistema de Gestión de Auditorías Aeronáuticas',
            email: 'Correo Electrónico',
            password: 'Contraseña',
            signIn: 'Iniciar Sesión',
            smsReport: 'Reporte Voluntario SMS',
            security: 'AES-256 Encriptado',
            forgotPassword: '¿Olvidaste tu contraseña?',
        },
        en: {
            title: 'OnTrackIA V1-Core',
            subtitle: 'Aviation Audit Management System',
            email: 'Email Address',
            password: 'Password',
            signIn: 'Sign In',
            smsReport: 'Voluntary SMS Report',
            security: 'AES-256 Encrypted',
            forgotPassword: 'Forgot your password?',
        },
    };

    const t = translations[language];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        // TODO: Implement login logic
    };

    return (
        <div className="login-container">
            {/* Background */}
            <div className="login-background"></div>

            {/* Header Controls */}
            <div className="login-header">
                <div className="login-logo">
                    <Shield size={32} className="text-info" />
                    <span className="text-mono font-bold text-xl">OnTrackIA</span>
                </div>
                <div className="login-controls">
                    {/* Language Selector */}
                    <div className="language-selector">
                        <button
                            className={language === 'es' ? 'active' : ''}
                            onClick={() => setLanguage('es')}
                        >
                            ES
                        </button>
                        <button
                            className={language === 'en' ? 'active' : ''}
                            onClick={() => setLanguage('en')}
                        >
                            EN
                        </button>
                    </div>
                    {/* Theme Toggle */}
                    <ThemeToggle />
                </div>
            </div>

            {/* Main Content */}
            <div className="login-content">
                {/* Title */}
                <div className="login-title">
                    <h1 className="text-4xl font-bold text-primary mb-2">{t.title}</h1>
                    <p className="text-secondary">{t.subtitle}</p>
                </div>

                {/* SMS Quick Report Button */}
                <button
                    onClick={() => setShowSMSReport(true)}
                    className="sms-quick-report-btn"
                >
                    <AlertTriangle size={20} />
                    <span>{t.smsReport}</span>
                </button>

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="email" className="form-label">
                            {t.email}
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            className="form-input"
                            required
                            autoComplete="email"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password" className="form-label">
                            {t.password}
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            className="form-input"
                            required
                            autoComplete="current-password"
                        />
                    </div>

                    <button type="submit" className="login-button">
                        <LogIn size={20} />
                        <span>{t.signIn}</span>
                    </button>

                    <a href="/forgot-password" className="forgot-password-link">
                        {t.forgotPassword}
                    </a>
                </form>

                {/* Security Indicator */}
                <div className="security-indicator">
                    <Shield size={16} />
                    <span>{t.security}</span>
                </div>
            </div>

            {/* SMS Quick Report Modal */}
            {showSMSReport && (
                <SMSQuickReport
                    onClose={() => setShowSMSReport(false)}
                    language={language}
                />
            )}
        </div>
    );
};

export default Login;
