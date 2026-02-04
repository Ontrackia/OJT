import React from 'react';
import { Wifi, WifiOff, Shield, AlertTriangle } from 'lucide-react';

interface StatusBarProps {
    language: 'es' | 'en';
    isOnline: boolean;
    onLanguageChange: (lang: 'es' | 'en') => void;
    onSMSReportClick: () => void;
}

const StatusBar: React.FC<StatusBarProps> = ({
    language,
    isOnline,
    onLanguageChange,
    onSMSReportClick,
}) => {
    return (
        <div className="status-bar">
            {/* Left Section */}
            <div className="status-bar-section">
                {/* Language Selector */}
                <div className="language-selector">
                    <button
                        className={language === 'es' ? 'active' : ''}
                        onClick={() => onLanguageChange('es')}
                    >
                        ES
                    </button>
                    <button
                        className={language === 'en' ? 'active' : ''}
                        onClick={() => onLanguageChange('en')}
                    >
                        EN
                    </button>
                </div>

                {/* Offline Indicator */}
                <div className={`offline-indicator ${isOnline ? 'online' : 'offline'}`}>
                    {isOnline ? (
                        <>
                            <Wifi size={16} />
                            <span>{language === 'es' ? 'En Línea' : 'Online'}</span>
                        </>
                    ) : (
                        <>
                            <WifiOff size={16} />
                            <span>{language === 'es' ? 'Modo Offline' : 'Offline Mode'}</span>
                        </>
                    )}
                </div>
            </div>

            {/* Right Section */}
            <div className="status-bar-section">
                {/* SMS Quick Report Button */}
                <button
                    onClick={onSMSReportClick}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-lg hover:from-orange-600 hover:to-red-600 transition shadow-lg"
                >
                    <AlertTriangle size={18} />
                    <span>{language === 'es' ? 'Reporte Voluntario SMS' : 'Voluntary SMS Report'}</span>
                </button>
            </div>
        </div>
    );
};

export default StatusBar;
