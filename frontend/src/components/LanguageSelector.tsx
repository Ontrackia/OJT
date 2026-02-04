import React from 'react';
import { useTranslation } from 'react-i18next';

interface LanguageSelectorProps {
    className?: string;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ className = '' }) => {
    const { i18n } = useTranslation();

    const changeLanguage = (lng: 'es' | 'en') => {
        i18n.changeLanguage(lng);
    };

    return (
        <div className={`language-selector ${className}`}>
            <button
                className={i18n.language === 'es' ? 'active' : ''}
                onClick={() => changeLanguage('es')}
                aria-label="Español"
            >
                ES
            </button>
            <button
                className={i18n.language === 'en' ? 'active' : ''}
                onClick={() => changeLanguage('en')}
                aria-label="English"
            >
                EN
            </button>
        </div>
    );
};

export default LanguageSelector;
