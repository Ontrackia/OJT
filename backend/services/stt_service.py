#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Speech-to-Text Service
============================================
Servicio STT para reportes por voz con detección de palabras clave

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

import speech_recognition as sr
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime

class STTService:
    """
    Servicio de Speech-to-Text para reportes técnicos por voz
    """
    
    # Palabras clave de discrepancia (ES/EN)
    DISCREPANCY_KEYWORDS = {
        'es': [
            'fisura', 'grieta', 'fractura',
            'fuga', 'escape', 'derrame',
            'desgaste', 'erosión', 'corrosión',
            'oxidación', 'deterioro',
            'aflojado', 'suelto', 'flojo',
            'dañado', 'roto', 'averiado',
            'pérdida', 'ausente', 'faltante',
            'excesivo', 'anormal', 'irregular'
        ],
        'en': [
            'crack', 'fracture', 'fissure',
            'leak', 'leakage', 'seepage',
            'wear', 'erosion', 'corrosion',
            'oxidation', 'deterioration',
            'loose', 'loosened', 'slack',
            'damaged', 'broken', 'defective',
            'loss', 'missing', 'absent',
            'excessive', 'abnormal', 'irregular'
        ]
    }
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Ajustar para ambientes ruidosos (hangares)
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0
    
    def transcribe_from_file(
        self,
        audio_file: Path,
        language: str = 'es'
    ) -> Dict:
        """
        Transcribe audio desde archivo
        
        Args:
            audio_file: Ruta al archivo de audio
            language: Idioma ('es' o 'en')
        
        Returns:
            Dict con transcripción y análisis
        """
        try:
            with sr.AudioFile(str(audio_file)) as source:
                # Ajustar ruido ambiental
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Grabar audio
                audio = self.recognizer.record(source)
            
            # Transcribir
            lang_code = 'es-ES' if language == 'es' else 'en-US'
            text = self.recognizer.recognize_google(audio, language=lang_code)
            
            # Analizar palabras clave
            analysis = self._analyze_text(text, language)
            
            return {
                'success': True,
                'transcription': text,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                **analysis
            }
        
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Could not understand audio',
                'transcription': '',
                'discrepancies_found': [],
                'criticality': 'unknown'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'API error: {e}',
                'transcription': '',
                'discrepancies_found': [],
                'criticality': 'unknown'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'transcription': '',
                'discrepancies_found': [],
                'criticality': 'unknown'
            }
    
    def transcribe_from_webm(
        self,
        webm_data: bytes,
        language: str = 'es'
    ) -> Dict:
        """
        Transcribe audio desde blob WebM del navegador
        
        Args:
            webm_data: Datos de audio en formato WebM
            language: Idioma
        
        Returns:
            Dict con transcripción y análisis
        """
        # Guardar temporalmente
        temp_file = Path('/tmp') / f'voice_report_{datetime.now().timestamp()}.webm'
        
        try:
            with open(temp_file, 'wb') as f:
                f.write(webm_data)
            
            # Convertir WebM a WAV con ffmpeg si es necesario
            # Por ahora, asumimos que speech_recognition puede manejar WebM
            
            result = self.transcribe_from_file(temp_file, language)
            
            return result
        
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
    
    def _analyze_text(self, text: str, language: str) -> Dict:
        """
        Analiza el texto buscando palabras clave de discrepancia
        
        Args:
            text: Texto transcrito
            language: Idioma
        
        Returns:
            Dict con análisis
        """
        text_lower = text.lower()
        keywords = self.DISCREPANCY_KEYWORDS.get(language, [])
        
        # Buscar palabras clave
        found_keywords = [
            kw for kw in keywords 
            if kw in text_lower
        ]
        
        # Determinar criticidad
        if len(found_keywords) >= 3:
            criticality = 'high'
        elif len(found_keywords) >= 1:
            criticality = 'medium'
        else:
            criticality = 'low'
        
        return {
            'discrepancies_found': found_keywords,
            'discrepancy_count': len(found_keywords),
            'criticality': criticality,
            'requires_review': len(found_keywords) > 0
        }
    
    def stream_transcribe(self, microphone_index: Optional[int] = None) -> Dict:
        """
        Transcribe en tiempo real desde micrófono
        
        Args:
            microphone_index: Índice del micrófono (None = default)
        
        Returns:
            Dict con transcripción
        """
        try:
            with sr.Microphone(device_index=microphone_index) as source:
                print("Ajustando ruido ambiental...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print("Escuchando...")
                audio = self.recognizer.listen(source, timeout=30, phrase_time_limit=60)
                
                print("Transcribiendo...")
                text = self.recognizer.recognize_google(audio, language='es-ES')
                
                return {
                    'success': True,
                    'transcription': text,
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'transcription': ''
            }

# Ejemplo de uso
if __name__ == "__main__":
    stt = STTService()
    
    # Simular transcripción
    test_audio = Path("test_voice_report.wav")
    
    if test_audio.exists():
        result = stt.transcribe_from_file(test_audio, language='es')
        
        print("\n" + "="*70)
        print("STT ANALYSIS")
        print("="*70)
        print(f"Transcription: {result.get('transcription', '')}")
        print(f"Discrepancies: {result.get('discrepancies_found', [])}")
        print(f"Criticality: {result.get('criticality', 'unknown')}")
        print("="*70 + "\n")
