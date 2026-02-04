/**
 * i18n Configuration for OnTrackIA V1-Core
 * Bilingual support (ES/EN)
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import es from './locales/es.json';
import en from './locales/en.json';

i18n
    .use(initReactI18next)
    .init({
        resources: {
            es: { translation: es },
            en: { translation: en },
        },
        lng: localStorage.getItem('ontrackia-language') || 'es',
        fallbackLng: 'es',
        interpolation: {
            escapeValue: false,
        },
    });

// Save language preference
i18n.on('languageChanged', (lng) => {
    localStorage.setItem('ontrackia-language', lng);
    document.documentElement.setAttribute('lang', lng);
});

export default i18n;
