/**
 * OnTrackIA OJT V2.0 - Chatbot Coach Component
 * =============================================
 * Asistente IA persistente basado en Mistral para guiar técnicos
 * 
 * Features:
 * - Diseño Deep Purple minimalista
 * - Conexión a Mistral AI
 * - Soporte ES/EN
 * - Logging forense SHA-256
 * - Protocolo de entrevista crítica
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, X, Minimize2, Maximize2, Activity } from 'lucide-react';
import { useLanguage } from './LanguageSelector';

const ChatbotCoach = ({ userId, currentTask, onInterviewComplete }) => {
    const { t, language } = useLanguage();
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [interviewMode, setInterviewMode] = useState(false);
    const [interviewProgress, setInterviewProgress] = useState(0);
    const [interviewAnswers, setInterviewAnswers] = useState({});
    const messagesEndRef = useRef(null);

    // Preguntas de entrevista crítica
    const CRITICAL_INTERVIEW_QUESTIONS = {
        es: [
            {
                id: 'resources',
                question: '¿Contaste con todas las herramientas y recursos necesarios para realizar esta tarea de forma segura?',
                category: 'Recursos'
            },
            {
                id: 'fatigue',
                question: '¿Te sentiste fatigado o bajo presión de tiempo durante la ejecución de esta tarea?',
                category: 'Fatiga/Presión'
            },
            {
                id: 'depth',
                question: 'Describe brevemente el procedimiento técnico que seguiste, incluyendo referencias AMM o ATA.',
                category: 'Profundidad Técnica'
            }
        ],
        en: [
            {
                id: 'resources',
                question: 'Did you have all the necessary tools and resources to perform this task safely?',
                category: 'Resources'
            },
            {
                id: 'fatigue',
                question: 'Did you feel fatigued or under time pressure during the execution of this task?',
                category: 'Fatigue/Pressure'
            },
            {
                id: 'depth',
                question: 'Briefly describe the technical procedure you followed, including AMM or ATA references.',
                category: 'Technical Depth'
            }
        ]
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Si la tarea es crítica, iniciar entrevista automáticamente
        if (currentTask?.is_critical && !interviewMode) {
            startCriticalInterview();
        }
    }, [currentTask]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const startCriticalInterview = () => {
        setInterviewMode(true);
        setInterviewProgress(0);
        setInterviewAnswers({});

        const welcomeMessage = language === 'es'
            ? 'Esta es una tarea crítica. Antes de validar, necesito hacerte 3 preguntas de seguridad según ICAO Doc 9859.'
            : 'This is a critical task. Before validation, I need to ask you 3 safety questions per ICAO Doc 9859.';

        addMessage('assistant', welcomeMessage);

        // Hacer primera pregunta
        setTimeout(() => {
            askNextQuestion();
        }, 1000);
    };

    const askNextQuestion = () => {
        const questions = CRITICAL_INTERVIEW_QUESTIONS[language];
        const currentQuestion = questions[interviewProgress];

        if (currentQuestion) {
            addMessage('assistant', `[${currentQuestion.category}] ${currentQuestion.question}`);
        }
    };

    const handleInterviewAnswer = async (answer) => {
        const questions = CRITICAL_INTERVIEW_QUESTIONS[language];
        const currentQuestion = questions[interviewProgress];

        // Guardar respuesta
        const newAnswers = {
            ...interviewAnswers,
            [currentQuestion.id]: {
                question: currentQuestion.question,
                answer: answer,
                timestamp: new Date().toISOString()
            }
        };
        setInterviewAnswers(newAnswers);

        // Avanzar progreso
        const newProgress = interviewProgress + 1;
        setInterviewProgress(newProgress);

        if (newProgress < questions.length) {
            // Pregunta siguiente
            setTimeout(() => {
                askNextQuestion();
            }, 500);
        } else {
            // Entrevista completada
            completeInterview(newAnswers);
        }
    };

    const completeInterview = async (answers) => {
        setInterviewMode(false);

        const completionMessage = language === 'es'
            ? 'Entrevista completada. Las respuestas han sido registradas con sello forense SHA-256. Puedes proceder con la validación.'
            : 'Interview completed. Responses have been logged with SHA-256 forensic seal. You may proceed with validation.';

        addMessage('assistant', completionMessage);

        // Enviar al backend
        try {
            const response = await fetch('/api/ojt/interview/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    task_id: currentTask?.id,
                    answers: answers,
                    language: language
                })
            });

            if (response.ok) {
                const data = await response.json();
                // Notificar al componente padre
                onInterviewComplete?.(data.interview_token);
            }
        } catch (error) {
            console.error('Error completing interview:', error);
        }
    };

    const addMessage = (role, content) => {
        setMessages(prev => [...prev, {
            role,
            content,
            timestamp: new Date().toISOString()
        }]);
    };

    const sendMessage = async () => {
        if (!inputText.trim()) return;

        const userMessage = inputText.trim();
        setInputText('');

        // Agregar mensaje del usuario
        addMessage('user', userMessage);

        // Si estamos en modo entrevista, procesar respuesta
        if (interviewMode) {
            handleInterviewAnswer(userMessage);
            return;
        }

        // Modo chat normal - llamar a Mistral
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat/coach', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    user_id: userId,
                    language: language,
                    context: {
                        current_task: currentTask,
                        conversation_history: messages.slice(-10) // Últimos 10 mensajes
                    }
                })
            });

            if (response.ok) {
                const data = await response.json();
                addMessage('assistant', data.response);
            } else {
                addMessage('assistant', language === 'es'
                    ? 'Error al procesar tu mensaje. Intenta de nuevo.'
                    : 'Error processing your message. Please try again.'
                );
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('assistant', language === 'es'
                ? 'No pude conectar con el servicio. Verifica tu conexión.'
                : 'Could not connect to service. Check your connection.'
            );
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    if (!isOpen) {
        // Botón flotante
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="icon-button"
                style={{
                    position: 'fixed',
                    bottom: '24px',
                    right: '24px',
                    width: '56px',
                    height: '56px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, var(--primary), var(--primary-hover))',
                    boxShadow: '0 8px 24px rgba(124, 58, 237, 0.4)',
                    zIndex: 1000
                }}
                title="Coach IA"
            >
                <MessageSquare size={24} color="white" />
            </button>
        );
    }

    return (
        <div style={{
            position: 'fixed',
            bottom: isMinimized ? 'auto' : '24px',
            top: isMinimized ? '24px' : 'auto',
            right: '24px',
            width: isMinimized ? '320px' : '420px',
            height: isMinimized ? '60px' : '600px',
            background: 'var(--bg-deep)',
            backdropFilter: 'blur(20px)',
            border: '1px solid var(--glass-border)',
            borderRadius: '16px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
            zIndex: 1000,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
        }}>
            {/* Header */}
            <div style={{
                padding: '16px',
                background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.1), rgba(124, 58, 237, 0.05))',
                borderBottom: '1px solid var(--glass-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <MessageSquare size={20} color="var(--primary)" />
                    <div>
                        <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                            Senior Coach
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                            {language === 'es' ? 'Asistente IA' : 'AI Assistant'}
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                        onClick={() => setIsMinimized(!isMinimized)}
                        className="icon-button"
                        style={{ width: '32px', height: '32px' }}
                    >
                        {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
                    </button>
                    <button
                        onClick={() => setIsOpen(false)}
                        className="icon-button"
                        style={{ width: '32px', height: '32px' }}
                    >
                        <X size={16} />
                    </button>
                </div>
            </div>

            {!isMinimized && (
                <>
                    {/* Interview Progress */}
                    {interviewMode && (
                        <div style={{
                            padding: '12px 16px',
                            background: 'rgba(124, 58, 237, 0.05)',
                            borderBottom: '1px solid var(--glass-border)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px'
                        }}>
                            <Activity size={16} color="var(--primary)" />
                            <div style={{ flex: 1 }}>
                                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                                    {language === 'es' ? 'Entrevista Crítica' : 'Critical Interview'}
                                </div>
                                <div className="progress-bar" style={{ height: '4px' }}>
                                    <div
                                        className="progress-fill"
                                        style={{
                                            width: `${(interviewProgress / 3) * 100}%`,
                                            transition: 'width 0.3s'
                                        }}
                                    />
                                </div>
                            </div>
                            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--primary)' }}>
                                {interviewProgress}/3
                            </span>
                        </div>
                    )}

                    {/* Messages */}
                    <div style={{
                        flex: 1,
                        overflowY: 'auto',
                        padding: '16px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '12px'
                    }}>
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                style={{
                                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                    maxWidth: '80%',
                                    padding: '10px 14px',
                                    borderRadius: '12px',
                                    background: msg.role === 'user'
                                        ? 'linear-gradient(135deg, var(--primary), var(--primary-hover))'
                                        : 'var(--glass-bg)',
                                    border: msg.role === 'user' ? 'none' : '1px solid var(--glass-border)',
                                    color: msg.role === 'user' ? 'white' : 'var(--text-primary)',
                                    fontSize: '13px',
                                    lineHeight: 1.5
                                }}
                            >
                                {msg.content}
                            </div>
                        ))}

                        {isLoading && (
                            <div style={{
                                alignSelf: 'flex-start',
                                padding: '10px 14px',
                                borderRadius: '12px',
                                background: 'var(--glass-bg)',
                                border: '1px solid var(--glass-border)',
                                fontSize: '13px',
                                color: 'var(--text-secondary)'
                            }}>
                                {language === 'es' ? 'Escribiendo...' : 'Typing...'}
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div style={{
                        padding: '16px',
                        borderTop: '1px solid var(--glass-border)',
                        background: 'var(--glass-bg)'
                    }}>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <input
                                type="text"
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder={language === 'es' ? 'Escribe tu mensaje...' : 'Type your message...'}
                                disabled={isLoading}
                                style={{
                                    flex: 1,
                                    padding: '10px 14px',
                                    background: 'var(--bg-deep)',
                                    border: '1px solid var(--glass-border)',
                                    borderRadius: '8px',
                                    color: 'var(--text-primary)',
                                    fontSize: '13px',
                                    outline: 'none'
                                }}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={isLoading || !inputText.trim()}
                                className="icon-button"
                                style={{
                                    width: '44px',
                                    height: '44px',
                                    background: 'var(--primary)',
                                    opacity: (!inputText.trim() || isLoading) ? 0.5 : 1
                                }}
                            >
                                <Send size={18} color="white" />
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default ChatbotCoach;
