/**
 * Voice Service - Web Speech API Integration
 * Professional voice-to-text for field operations
 */

export interface VoiceCommand {
    text: string;
    confidence: number;
    timestamp: string;
}

export class VoiceService {
    private recognition: any; // SpeechRecognition
    private isRecording: boolean = false;
    private language: string = 'es-ES';

    constructor(language: 'es' | 'en' = 'es') {
        this.language = language === 'es' ? 'es-ES' : 'en-US';
        this.initRecognition();
    }

    private initRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('Speech Recognition not supported');
            return;
        }

        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
        this.recognition = new SpeechRecognition();

        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = this.language;
    }

    setLanguage(language: 'es' | 'en') {
        this.language = language === 'es' ? 'es-ES' : 'en-US';
        if (this.recognition) {
            this.recognition.lang = this.language;
        }
    }

    startRecording(
        onResult: (command: VoiceCommand) => void,
        onError?: (error: string) => void
    ) {
        if (!this.recognition) {
            onError?.('Speech Recognition not available');
            return;
        }

        this.isRecording = true;

        this.recognition.onresult = (event: any) => {
            const last = event.results.length - 1;
            const text = event.results[last][0].transcript;
            const confidence = event.results[last][0].confidence;

            // Process voice commands
            const processedText = this.processCommands(text);

            onResult({
                text: processedText,
                confidence,
                timestamp: new Date().toISOString(),
            });
        };

        this.recognition.onerror = (event: any) => {
            console.error('Speech recognition error:', event.error);
            onError?.(event.error);
            this.isRecording = false;
        };

        this.recognition.onend = () => {
            if (this.isRecording) {
                // Restart if still recording
                this.recognition.start();
            }
        };

        this.recognition.start();
    }

    stopRecording() {
        this.isRecording = false;
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    private processCommands(text: string): string {
        let processed = text;

        // Spanish commands
        if (this.language === 'es-ES') {
            processed = processed.replace(/punto y aparte/gi, '\n\n');
            processed = processed.replace(/nueva línea/gi, '\n');
            processed = processed.replace(/punto/gi, '.');
            processed = processed.replace(/coma/gi, ',');
            processed = processed.replace(/dos puntos/gi, ':');
            processed = processed.replace(/punto y coma/gi, ';');
        }

        // English commands
        if (this.language === 'en-US') {
            processed = processed.replace(/new paragraph/gi, '\n\n');
            processed = processed.replace(/new line/gi, '\n');
            processed = processed.replace(/period/gi, '.');
            processed = processed.replace(/comma/gi, ',');
            processed = processed.replace(/colon/gi, ':');
            processed = processed.replace(/semicolon/gi, ';');
        }

        return processed;
    }

    isSupported(): boolean {
        return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    }

    getRecordingStatus(): boolean {
        return this.isRecording;
    }
}

export const voiceService = new VoiceService();
