#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - AI Guardian Service
=========================================
Servicio de guardia que valida la integridad de las validaciones de tareas
antes de marcarlas como 'validated'.

Bloquea validaciones si:
- El reporte es superficial (menos de 200 palabras)
- Faltan coordenadas GPS
- No hay evidencias forenses
- Palabras prohibidas detectadas

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
Compliance: ICAO Doc 9859 + Protocolo Búnker
"""

import hashlib
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationGuardResult:
    """Resultado de la validación del guardia"""
    is_valid: bool
    score: int  # 0-100
    errors: List[str]
    warnings: List[str]
    recommendation: str

class AIGuardianService:
    """
    Servicio de guardia de IA que valida la calidad
    de los reportes antes de marcarlos como validados
    """
    
    # Palabras prohibidas (superficiales)
    FORBIDDEN_WORDS = [
        'arreglado', 'ok', 'listo', 'bien', 'todo ok',
        'fixed', 'done', 'good', 'all good'
    ]
    
    # Dirty Dozen keywords
    DIRTY_DOZEN_KEYWORDS = [
        'fatiga', 'fatigue',
        'complacencia', 'complacency',
        'presión', 'pressure',
        'distracción', 'distraction',
        'conocimiento', 'knowledge',
        'equipo', 'teamwork',
        'recursos', 'resources',
        'asertividad', 'assertiveness',
        'estrés', 'stress',
        'conciencia', 'awareness',
        'normas', 'norms',
        'comunicación', 'communication'
    ]
    
    # Términos técnicos aeronáuticos
    TECHNICAL_TERMS = [
        'ata', 'amm', 'ipc', 'srm', 'tsm',
        'faa', 'easa', 'icao', 'rac',
        'airworthiness', 'aeronavegabilidad',
        'turbina', 'turbine',
        'fuselaje', 'fuselage',
        'tren de aterrizaje', 'landing gear'
    ]
    
    def __init__(self, language: str = 'es'):
        self.language = language
    
    def validate_task_report(
        self,
        report_text: str,
        gps_coords: Optional[Dict[str, float]] = None,
        evidence_hash: Optional[str] = None,
        task_code: Optional[str] = None
    ) -> ValidationGuardResult:
        """
        Valida un reporte de tarea antes de marcarlo como validado
        
        Args:
            report_text: Texto del reporte técnico
            gps_coords: Coordenadas GPS {latitude, longitude, accuracy}
            evidence_hash: Hash SHA-256 de la evidencia
            task_code: Código de la tarea (ej: ATA-71-001)
        
        Returns:
            ValidationGuardResult con score y errores
        """
        errors = []
        warnings = []
        score = 100
        
        # 1. Verificar profundidad (mínimo 200 palabras)
        word_count = len(report_text.split())
        if word_count < 200:
            errors.append(
                f"Reporte superficial: {word_count} palabras (mínimo 200)" if self.language == 'es'
                else f"Superficial report: {word_count} words (minimum 200)"
            )
            score -= 30
        elif word_count < 300:
            warnings.append(
                "Reporte breve. Considera agregar más detalles técnicos." if self.language == 'es'
                else "Brief report. Consider adding more technical details."
            )
            score -= 10
        
        # 2. Verificar palabras prohibidas
        forbidden_found = [
            word for word in self.FORBIDDEN_WORDS
            if word in report_text.lower()
        ]
        if forbidden_found:
            errors.append(
                f"Palabras superficiales detectadas: {', '.join(forbidden_found)}" if self.language == 'es'
                else f"Superficial words detected: {', '.join(forbidden_found)}"
            )
            score -= 20
        
        # 3. Verificar profundidad técnica
        technical_found = sum(
            1 for term in self.TECHNICAL_TERMS
            if term in report_text.lower()
        )
        if technical_found == 0:
            errors.append(
                "Falta terminología técnica aeronáutica (ATA, AMM, FAA, etc.)" if self.language == 'es'
                else "Missing aeronautical technical terminology (ATA, AMM, FAA, etc.)"
            )
            score -= 25
        elif technical_found < 3:
            warnings.append(
                "Poca terminología técnica. Agrega referencias AMM/ATA." if self.language == 'es'
                else "Limited technical terminology. Add AMM/ATA references."
            )
            score -= 10
        
        # 4. Verificar GPS (obligatorio para trazabilidad Ultimate)
        if not gps_coords or not gps_coords.get('latitude') or not gps_coords.get('longitude'):
            errors.append(
                "Faltan coordenadas GPS. La geolocalización es obligatoria." if self.language == 'es'
                else "Missing GPS coordinates. Geolocation is mandatory."
            )
            score -= 30
        else:
            # Verificar precisión GPS
            accuracy = gps_coords.get('accuracy', 999)
            if accuracy > 100:
                warnings.append(
                    f"Precisión GPS baja: {accuracy}m (recomendado <50m)" if self.language == 'es'
                    else f"Low GPS accuracy: {accuracy}m (recommended <50m)"
                )
                score -= 5
        
        # 5. Verificar integridad forense (hash SHA-256)
        if not evidence_hash or len(evidence_hash) != 64:
            errors.append(
                "Falta sellado forense SHA-256 de la evidencia" if self.language == 'es'
                else "Missing forensic SHA-256 seal of evidence"
            )
            score -= 20
        
        # 6. Verificar mención de Dirty Dozen (recomendado)
        dirty_dozen_found = sum(
            1 for keyword in self.DIRTY_DOZEN_KEYWORDS
            if keyword in report_text.lower()
        )
        if dirty_dozen_found == 0:
            warnings.append(
                "No se mencionan factores humanos (Dirty Dozen)" if self.language == 'es'
                else "No mention of human factors (Dirty Dozen)"
            )
            score -= 5
        
        # Asegurar que score no sea negativo
        score = max(0, score)
        
        # Determinar si es válido (score >= 70)
        is_valid = score >= 70 and len(errors) == 0
        
        # Generar recomendación
        if is_valid:
            recommendation = (
                f"VERIFICADO: Reporte apto para certificación aeronáutica (Score: {score}/100)" if self.language == 'es'
                else f"VERIFIED: Report suitable for aeronautical certification (Score: {score}/100)"
            )
        else:
            recommendation = (
                f"RECHAZADO: El reporte no cumple con los estándares ICAO Doc 9859 (Score: {score}/100). " +
                "Corrija los errores antes de validar." if self.language == 'es'
                else f"REJECTED: Report does not meet ICAO Doc 9859 standards (Score: {score}/100). " +
                "Fix errors before validation."
            )
        
        return ValidationGuardResult(
            is_valid=is_valid,
            score=score,
            errors=errors,
            warnings=warnings,
            recommendation=recommendation
        )
    
    def print_validation_result(self, result: ValidationGuardResult):
        """Imprime el resultado en consola con formato Deep Purple"""
        print("\n" + "="*70)
        print(f"{'🔐 AUDITORÍA DE GUARDIA IA' if self.language == 'es' else '🔐 AI GUARDIAN AUDIT'}")
        print("="*70)
        
        print(f"\n{'Score de Calidad' if self.language == 'es' else 'Quality Score'}: {result.score}/100")
        print(f"{'Estado' if self.language == 'es' else 'Status'}: {'✅ VÁLIDO' if result.is_valid else '❌ RECHAZADO'}")
        
        if result.errors:
            print(f"\n{'❌ ERRORES CRÍTICOS:' if self.language == 'es' else '❌ CRITICAL ERRORS:'}")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print(f"\n{'⚠️  ADVERTENCIAS:' if self.language == 'es' else '⚠️  WARNINGS:'}")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        print(f"\n{'💡 RECOMENDACIÓN:' if self.language == 'es' else '💡 RECOMMENDATION:'}")
        print(f"  {result.recommendation}")
        
        print("\n" + "="*70)

# Ejemplo de uso
if __name__ == "__main__":
    guardian = AIGuardianService(language='es')
    
    # Test 1: Reporte superficial (debe fallar)
    print("\n📋 Test 1: Reporte Superficial")
    result1 = guardian.validate_task_report(
        report_text="Todo ok. Tarea arreglada.",
        gps_coords=None,
        evidence_hash=None
    )
    guardian.print_validation_result(result1)
    
    # Test 2: Reporte completo (debe pasar)
    print("\n📋 Test 2: Reporte Completo")
    complete_report = """
    Se realizó inspección completa del motor turbofan CFM56-7B según AMM 71-00-00.
    
    Procedimiento:
    1. Verificación visual de álabes (AMM 71-21-01)
    2. Medición de clearances según TSM 71-00-00-810-801
    3. Inspección boroscopica de cámara de combustión
    
    Hallazgos:
    - FOD menor en álabe #12 del compresor (ATA 71)
    - Clearance del labyrinth seal dentro de límites (0.015" - 0.020")
    - No se detectaron grietas ni erosión anormal
    
    Factores Humanos:
    - Trabajo realizado con iluminación adecuada (recursos)
    - Comunicación efectiva con inspector senior (trabajo en equipo)
    - Se siguió procedimiento AMM sin desviaciones (normas)
    
    Herramientas utilizadas:
    - Boroscopio Olympus IPLEX NX
    - Feeler gauge set 0.001"-0.025"
    - Torquímetro calibrado (cert. vigente)
    
    Referencias:
    - AMM CFM56-7B 71-00-00
    - EASA Part-145 MOE Chapter 2.5
    - ICAO Doc 9859 SMS framework
    
    Tiempo total: 3.5 horas
    Validado por: Inspector Senior Carlos Rodríguez (Stamp #AMT-2020-045)
    """
    
    result2 = guardian.validate_task_report(
        report_text=complete_report,
        gps_coords={
            'latitude': 13.692940,
            'longitude': -89.218191,
            'accuracy': 12.5
        },
        evidence_hash='a7f3c9e42d1b8f6a91c2d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5',
        task_code='ATA-71-001'
    )
    guardian.print_validation_result(result2)
