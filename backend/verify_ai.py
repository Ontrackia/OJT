#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Verify AI Governance
==========================================
Script de auditoría para validar que Mistral AI cumple con los 4 Pilares
de Gobernanza del "Senior Auditor Coach" basado en ICAO Doc 9859.

Pilares de Gobernanza:
1. Profundidad Técnica (Score >= 7/10)
2. No Superficialidad (respuestas > 200 palabras técnicas)
3. Dirty Dozen (validación de factores humanos)
4. Trazabilidad (referencias a normativa)

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
Compliance: RAC LPTA 66, UK CAA CAP 741, AAC F1/F2
"""

import os
import sys
import json
import re
from typing import Dict, List, Tuple
from datetime import datetime
import requests
from dataclasses import dataclass

# ==========================================
# CONFIGURACIÓN
# ==========================================
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
MISTRAL_ENDPOINT = os.getenv("MISTRAL_ENDPOINT", "https://api.mistral.ai/v1/chat/completions")

# Umbrales de gobernanza
MIN_DEPTH_SCORE = int(os.getenv("AI_GOVERNANCE_MIN_DEPTH_SCORE", "7"))
MIN_WORD_COUNT = 200
DIRTY_DOZEN_KEYWORDS = [
    "fatiga", "complacencia", "presión", "distracción",
    "falta de conocimiento", "falta de trabajo en equipo",
    "falta de recursos", "falta de asertividad",
    "estrés", "falta de conciencia situacional",
    "normas", "procedimientos"
]

@dataclass
class GovernanceResult:
    """Resultado de auditoría de gobernanza"""
    passed: bool
    depth_score: int
    word_count: int
    dirty_dozen_found: List[str]
    has_traceability: bool
    recommendations: List[str]
    timestamp: str

class MistralAIGovernanceAuditor:
    """
    Auditor de Gobernanza para Mistral AI
    Valida que las respuestas cumplan con protocolos aeronáuticos
    """
    
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise ValueError("❌ MISTRAL_API_KEY no configurada en .env")
        self.api_key = MISTRAL_API_KEY
        self.model = MISTRAL_MODEL
        self.endpoint = MISTRAL_ENDPOINT
    
    def call_mistral(self, prompt: str, max_tokens: int = 2048) -> str:
        """
        Llama a Mistral AI API
        
        Args:
            prompt: Prompt para el modelo
            max_tokens: Máximo de tokens en la respuesta
        
        Returns:
            Respuesta del modelo
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un Senior Auditor Coach especializado en mantenimiento aeronáutico basado en ICAO Doc 9859. Proporciona análisis técnicos profundos con referencias a normativa."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"❌ Error llamando a Mistral API: {str(e)}")
    
    def calculate_depth_score(self, response: str) -> int:
        """
        Calcula profundidad técnica de la respuesta (1-10)
        
        Criterios:
        - Uso de terminología técnica
        - Referencias a normativa
        - Estructura lógica
        - Ejemplos concretos
        """
        score = 0
        response_lower = response.lower()
        
        # Terminología técnica aeronáutica (+3 puntos)
        technical_terms = [
            "ata", "amm", "faa", "easa", "airworthiness", "aeronavegabilidad",
            "mro", "mel", "ndt", "ad", "sb", "inspection", "compliance",
            "maintenance", "overhaul", "troubleshooting", "component"
        ]
        terms_found = sum(1 for term in technical_terms if term in response_lower)
        score += min(3, terms_found // 3)
        
        # Referencias a normativa (+3 puntos)
        regulatory_refs = [
            "icao", "doc 9859", "rac lpta", "cap 741", "part 145",
            "appendix", "chapter", "section"
        ]
        refs_found = sum(1 for ref in regulatory_refs if ref in response_lower)
        score += min(3, refs_found // 2)
        
        # Estructura y ejemplos (+2 puntos)
        has_structure = any(marker in response for marker in ["1.", "2.", "-", "•"])
        has_examples = any(word in response_lower for word in ["ejemplo", "example", "caso", "case"])
        score += 1 if has_structure else 0
        score += 1 if has_examples else 0
        
        # Longitud y detalle (+2 puntos)
        word_count = len(response.split())
        if word_count > 400:
            score += 2
        elif word_count > 200:
            score += 1
        
        return min(10, score)
    
    def check_dirty_dozen(self, response: str) -> List[str]:
        """
        Verifica mención de factores humanos (Dirty Dozen)
        
        Returns:
            Lista de factores mencionados
        """
        response_lower = response.lower()
        found = [
            keyword for keyword in DIRTY_DOZEN_KEYWORDS
            if keyword in response_lower
        ]
        return found
    
    def check_traceability(self, response: str) -> bool:
        """
        Verifica que la respuesta tenga referencias trazables
        
        Returns:
            True si hay referencias a normativa o documentos
        """
        response_lower = response.lower()
        traceability_patterns = [
            r"(rac|faa|easa|icao|ata)[\s-]?\d+",  # RAC-145, EASA Part-145, etc.
            r"(doc|document|appendix|chapter|section)[\s-]?\d+",
            r"(amm|ipc|srm|tsm)[\s-]?\d{2,}",  # Manuales técnicos
        ]
        
        for pattern in traceability_patterns:
            if re.search(pattern, response_lower):
                return True
        
        return False
    
    def audit_response(self, prompt: str) -> GovernanceResult:
        """
        Audita una respuesta completa de Mistral AI
        
        Args:
            prompt: Pregunta técnica
        
        Returns:
            Resultado de auditoría
        """
        print(f"\n📋 Auditando respuesta para: '{prompt[:60]}...'")
        
        # Obtener respuesta
        response = self.call_mistral(prompt)
        
        # Calcular métricas
        depth_score = self.calculate_depth_score(response)
        word_count = len(response.split())
        dirty_dozen_found = self.check_dirty_dozen(response)
        has_traceability = self.check_traceability(response)
        
        # Validar umbrales
        passed = True
        recommendations = []
        
        if depth_score < MIN_DEPTH_SCORE:
            passed = False
            recommendations.append(f"❌ Profundidad técnica insuficiente: {depth_score}/10 (mínimo: {MIN_DEPTH_SCORE}/10)")
        
        if word_count < MIN_WORD_COUNT:
            passed = False
            recommendations.append(f"❌ Respuesta superficial: {word_count} palabras (mínimo: {MIN_WORD_COUNT})")
        
        if not has_traceability:
            passed = False
            recommendations.append("❌ Falta trazabilidad: No hay referencias a normativa")
        
        if len(dirty_dozen_found) < 2:
            recommendations.append(f"⚠️  Poca mención de factores humanos (Dirty Dozen): {len(dirty_dozen_found)} factores")
        
        return GovernanceResult(
            passed=passed,
            depth_score=depth_score,
            word_count=word_count,
            dirty_dozen_found=dirty_dozen_found,
            has_traceability=has_traceability,
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def print_report(self, result: GovernanceResult):
        """Imprime reporte de auditoría"""
        print("\n" + "="*60)
        print("📊 REPORTE DE AUDITORÍA AI GOVERNANCE")
        print("="*60)
        print(f"⏰ Timestamp: {result.timestamp}")
        print(f"✅ Estado: {'APROBADO' if result.passed else '❌ RECHAZADO'}")
        print(f"📈 Profundidad Técnica: {result.depth_score}/10")
        print(f"📝 Palabras: {result.word_count}")
        print(f"🔗 Trazabilidad: {'✓' if result.has_traceability else '✗'}")
        print(f"👥 Dirty Dozen Mencionados: {len(result.dirty_dozen_found)}")
        
        if result.dirty_dozen_found:
            print(f"   - {', '.join(result.dirty_dozen_found)}")
        
        if result.recommendations:
            print("\n⚠️  Recomendaciones:")
            for rec in result.recommendations:
                print(f"   {rec}")
        
        print("="*60 + "\n")

def run_full_governance_check():
    """
    Ejecuta verificación completa de gobernanza
    """
    print("\n🔐 OnTrackIA OJT V2.0 - Verify AI Governance")
    print("="*60)
    
    auditor = MistralAIGovernanceAuditor()
    
    # Test prompts (casos representativos)
    test_prompts = [
        "Explica el procedimiento de inspección de un motor turbofán según ATA 71",
        "¿Cómo se realiza una RCA (Root Cause Analysis) de un hallazgo de auditoría según ICAO Doc 9859?",
        "Describe los factores humanos que pueden causar un error de mantenimiento"
    ]
    
    results = []
    for prompt in test_prompts:
        try:
            result = auditor.audit_response(prompt)
            auditor.print_report(result)
            results.append(result)
        except Exception as e:
            print(f"❌ Error en auditoría: {str(e)}")
            return False
    
    # Resumen final
    passed_count = sum(1 for r in results if r.passed)
    avg_depth = sum(r.depth_score for r in results) / len(results)
    
    print("\n🏁 RESUMEN FINAL")
    print("="*60)
    print(f"Tests aprobados: {passed_count}/{len(results)}")
    print(f"Profundidad promedio: {avg_depth:.1f}/10")
    
    if passed_count == len(results) and avg_depth >= MIN_DEPTH_SCORE:
        print("\n✅ GOBERNANCIA AI VERIFICADA - Sistema listo para producción")
        return True
    else:
        print("\n❌ GOBERNANCIA AI NO CUMPLE - Requiere ajustes en configuración")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify AI Governance")
    parser.add_argument("--check-governance", action="store_true", help="Run full governance check")
    parser.add_argument("--full-check", action="store_true", help="Alias for --check-governance")
    
    args = parser.parse_args()
    
    if args.check_governance or args.full_check:
        success = run_full_governance_check()
        sys.exit(0 if success else 1)
    else:
        print("Uso: python verify_ai.py --check-governance")
        sys.exit(1)
