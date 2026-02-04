/**
 * OnTrackIA OJT V2.0 - Theme Selector Component
 * ==============================================
 * Selector de tema Día (Alto Contraste) / Noche (Deep Purple)
 * 
 * Modos:
 * - Día: Fondo blanco, texto negro, contraste alto
 * - Noche: Fondo #0a051a, texto blanco, Glassmorphism
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';

const ThemeSelector = () => {
    const [theme, setTheme] = useState('night'); // 'day' or 'night'

    useEffect(() => {
        // Cargar tema guardado
        const savedTheme = localStorage.getItem('ontrackia-theme') || 'night';
        setTheme(savedTheme);
        applyTheme(savedTheme);
    }, []);

    const applyTheme = (selectedTheme) => {
        const root = document.documentElement;

        if (selectedTheme === 'day') {
            // Modo Día - Alto Contraste
            root.style.setProperty('--primary', '#5b21b6');
            root.style.setProperty('--primary-hover', '#6d28d9');
            root.style.setProperty('--primary-active', '#4c1d95');

            root.style.setProperty('--bg-deep', '#ffffff');
            root.style.setProperty('--bg-card', '#f8fafc');
            root.style.setProperty('--bg-card-hover', '#f1f5f9');

            root.style.setProperty('--glass-bg', 'rgba(0, 0, 0, 0.02)');
            root.style.setProperty('--glass-border', 'rgba(0, 0, 0, 0.1)');
            root.style.setProperty('--glass-shadow', '0 4px 12px 0 rgba(0, 0, 0, 0.1)');

            root.style.setProperty('--text-primary', '#0f172a');
            root.style.setProperty('--text-secondary', '#475569');
            root.style.setProperty('--text-muted', '#64748b');
        } else {
            // Modo Noche - Deep Purple
            root.style.setProperty('--primary', '#7c3aed');
            root.style.setProperty('--primary-hover', '#6d28d9');
            root.style.setProperty('--primary-active', '#5b21b6');

            root.style.setProperty('--bg-deep', '#0a051a');
            root.style.setProperty('--bg-card', 'rgba(124, 58, 237, 0.05)');
            root.style.setProperty('--bg-card-hover', 'rgba(124, 58, 237, 0.08)');

            root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.05)');
            root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.1)');
            root.style.setProperty('--glass-shadow', '0 8px 32px 0 rgba(31, 38, 135, 0.37)');

            root.style.setProperty('--text-primary', '#ffffff');
            root.style.setProperty('--text-secondary', '#cbd5e1');
            root.style.setProperty('--text-muted', '#94a3b8');
        }
    };

    const toggleTheme = () => {
        const newTheme = theme === 'day' ? 'night' : 'day';
        setTheme(newTheme);
        applyTheme(newTheme);
        localStorage.setItem('ontrackia-theme', newTheme);
    };

    return (
        <button
            onClick={toggleTheme}
            className="icon-button"
            title={theme === 'day' ? 'Cambiar a Modo Noche' : 'Cambiar a Modo Día'}
            style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '0 16px'
            }}
        >
            {theme === 'day' ? (
                <>
                    <Moon size={20} />
                    <span style={{ fontSize: '14px' }}>Noche</span>
                </>
            ) : (
                <>
                    <Sun size={20} />
                    <span style={{ fontSize: '14px' }}>Día</span>
                </>
            )}
        </button>
    );
};

export default ThemeSelector;
