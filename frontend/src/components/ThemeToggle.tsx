import React, { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
    className?: string;
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '' }) => {
    const [theme, setTheme] = useState<'light' | 'dark'>('dark');

    // Initialize theme from localStorage or user preference
    useEffect(() => {
        const savedTheme = localStorage.getItem('ontrackia-theme') as 'light' | 'dark' | null;
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
        setTheme(initialTheme);
        applyTheme(initialTheme);
    }, []);

    const applyTheme = (newTheme: 'light' | 'dark') => {
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('ontrackia-theme', newTheme);
    };

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        applyTheme(newTheme);

        // TODO: Sync to user profile in PostgreSQL
        syncThemeToServer(newTheme);
    };

    const syncThemeToServer = async (theme: 'light' | 'dark') => {
        try {
            await fetch('/api/v2/user/preferences', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
                body: JSON.stringify({ theme }),
            });
        } catch (error) {
            console.error('Failed to sync theme to server:', error);
        }
    };

    return (
        <button
            onClick={toggleTheme}
            className={`theme-toggle ${className}`}
            aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            title={theme === 'light' ? 'Night Mode' : 'Day Mode'}
        >
            <div className="theme-toggle-track">
                <div className={`theme-toggle-thumb ${theme}`}>
                    {theme === 'light' ? (
                        <Sun size={16} className="theme-icon" />
                    ) : (
                        <Moon size={16} className="theme-icon" />
                    )}
                </div>
            </div>
        </button>
    );
};

export default ThemeToggle;
