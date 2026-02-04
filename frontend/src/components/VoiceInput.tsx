import React, { useState, useEffect } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { voiceService, VoiceCommand } from '../services/voice.service';

interface VoiceInputProps {
    value: string;
    onChange: (value: string) => void;
    language?: 'es' | 'en';
    placeholder?: string;
    className?: string;
}

const VoiceInput: React.FC<VoiceInputProps> = ({
    value,
    onChange,
    language = 'es',
    placeholder,
    className = '',
}) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isSupported, setIsSupported] = useState(true);

    useEffect(() => {
        setIsSupported(voiceService.isSupported());
        voiceService.setLanguage(language);
    }, [language]);

    const toggleRecording = () => {
        if (isRecording) {
            voiceService.stopRecording();
            setIsRecording(false);
        } else {
            voiceService.startRecording(
                (command: VoiceCommand) => {
                    onChange(value + (value ? ' ' : '') + command.text);
                },
                (error: string) => {
                    console.error('Voice error:', error);
                    setIsRecording(false);
                }
            );
            setIsRecording(true);
        }
    };

    if (!isSupported) {
        return (
            <div className="voice-input-unsupported">
                <p className="text-sm text-secondary">
                    {language === 'es'
                        ? 'Dictado por voz no disponible en este navegador'
                        : 'Voice dictation not available in this browser'}
                </p>
            </div>
        );
    }

    return (
        <div className={`voice-input-container ${className}`}>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                className="voice-input-textarea"
                rows={6}
            />

            <button
                type="button"
                onClick={toggleRecording}
                className={`voice-input-button ${isRecording ? 'recording' : ''}`}
                title={isRecording
                    ? (language === 'es' ? 'Detener grabación' : 'Stop recording')
                    : (language === 'es' ? 'Iniciar grabación' : 'Start recording')
                }
            >
                {isRecording ? (
                    <>
                        <div className="voice-waveform">
                            <div className="voice-waveform-bar"></div>
                            <div className="voice-waveform-bar"></div>
                            <div className="voice-waveform-bar"></div>
                            <div className="voice-waveform-bar"></div>
                            <div className="voice-waveform-bar"></div>
                        </div>
                        <span className="ml-2">
                            {language === 'es' ? 'Grabando...' : 'Recording...'}
                        </span>
                    </>
                ) : (
                    <>
                        <Mic size={20} />
                        <span className="ml-2">
                            {language === 'es' ? 'Dictar' : 'Dictate'}
                        </span>
                    </>
                )}
            </button>
        </div>
    );
};

export default VoiceInput;
