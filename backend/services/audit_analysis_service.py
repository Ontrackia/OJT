#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Audit Analysis Service (Multi-Agent System)
=================================================================
Orquestador de agentes de IA para análisis de evidencias

Agentes Activos:
- Senior Auditor Coach: Análisis RAG de compliance normativo

Agentes Futuros (Extensible):
- Visual Inspector: Computer vision de imágenes
- Risk Assessor: Patrones de error humano
- Regulatory Monitor: Vigilancia proactiva
- Voice Analyzer: STT con detección estrés/fatiga

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import sys

# Importar ChromaDB para RAG
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

class SeniorAuditorCoachAgent:
    """
    Agente: Senior Auditor Coach
    ============================
    Análisis de compliance normativo usando RAG
    """
    
    def __init__(self, chroma_client=None):
        self.name = "Senior Auditor Coach"
        self.chroma_client = chroma_client
        self.collection = None
        
        if chroma_client:
            try:
                self.collection = chroma_client.get_collection(
                    name="ontrackia_knowledge"
                )
            except:
                print(f"[{self.name}] Warning: ChromaDB collection not found")
    
    def analyze(
        self,
        task_description: str,
        context: Dict,
        territory: str = None
    ) -> Dict:
        """
        Analiza tarea usando RAG de normativa mundial
        
        Args:
            task_description: Descripción de la tarea OJT
            context: Contexto adicional (aircraft, component, etc.)
            territory: Filtro territorial (CANADA, BRAZIL, etc.) - opcional
        
        Returns:
            Análisis con compliance score y referencias
        """
        # Construir query RAG
        query_text = self._build_rag_query(task_description, context)
        
        # Consultar ChromaDB (con filtro territorial si aplica)
        if self.collection:
            rag_results = self._query_rag(query_text, territory=territory)
        else:
            rag_results = self._mock_rag_results()
        
        # Calcular compliance score
        compliance_score = self._calculate_compliance(rag_results, context)
        
        # Detectar referencias normativas
        normative_refs = self._extract_normative_references(rag_results)
        
        # Identificar discrepancias
        discrepancies = self._identify_discrepancies(
            rag_results,
            context,
            compliance_score
        )
        
        # Clasificar nivel de riesgo
        risk_level = self._classify_risk_level(compliance_score)
        
        return {
            "agent": self.name,
            "compliance_score": compliance_score,
            "risk_level": risk_level,
            "normative_references": normative_refs,
            "discrepancies": discrepancies,
            "rag_insights": self._generate_insights(rag_results, territory),
            "confidence": rag_results.get('confidence', 0.75),
            "territory": territory or "GLOBAL"
        }
    
    def _build_rag_query(self, task_description: str, context: Dict) -> str:
        """Construye query optimizado para RAG"""
        aircraft = context.get('aircraft_type', 'aircraft')
        component = context.get('component', 'component')
        task_code = context.get('task_code', '')
        
        query = f"""
Task: {task_description}
Aircraft Type: {aircraft}
Component: {component}
Task Code: {task_code}

What are the regulatory requirements and compliance criteria?
"""
        return query.strip()
    
    def _query_rag(self, query_text: str, territory: str = None) -> Dict:
        """Ejecuta query en ChromaDB con filtro territorial opcional"""
        try:
            # Query sin filtros primero (para máxima cobertura)
            results = self.collection.query(
                query_texts=[query_text],
                n_results=20  # Más resultados para filtrado posterior
            )
            
            # Filtrar por categorías relevantes post-query si es necesario
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            # Priorizar documentos de auditoría y regulaciones
            relevant_categories = [
                'EASA_REGULATION',
                'FAA_REGULATION',
                'ICAO_STANDARD',
                'UK_CAA_REGULATION',
                'AUDIT_REQUIREMENT',
                'LAR_REGULATION'
            ]
            
            # Re-ordernar colocando categorías prioritarias primero
            sorted_results = list(zip(documents, metadatas, distances))
            sorted_results.sort(
                key=lambda x: (
                    # 1. Prioridad: match territorial exacto
                    x[1].get('territory') == territory if territory else False,
                    # 2. Prioridad: categoría relevante
                    x[1].get('category') in relevant_categories,
                    # 3. Prioridad: menor distance
                    -x[2]
                ),
                reverse=True
            )
            
            # Desempaquetar y tomar top 10
            if sorted_results:
                documents, metadatas, distances = zip(*sorted_results[:10])
                documents = list(documents)
                metadatas = list(metadatas)
                distances = list(distances)
            
            return {
                "documents": documents,
                "metadatas": metadatas,
                "distances": distances,
                "confidence": self._calculate_rag_confidence(results)
            }
        except Exception as e:
            print(f"[{self.name}] RAG query error: {e}")
            return self._mock_rag_results()
    
    def _mock_rag_results(self) -> Dict:
        """Resultados mock para testing sin ChromaDB"""
        return {
            "documents": [
                "EASA Part-66 Appendix I requires supervisor signature for critical tasks",
                "FAA Order 8900.1 specifies photographic evidence requirements",
                "ICAO Doc 9859 SMS framework requires risk assessment documentation"
            ],
            "metadatas": [
                {"authority": "EASA", "document": "Part-66", "criticality": "high"},
                {"authority": "FAA", "document": "Order 8900.1", "criticality": "medium"},
                {"authority": "ICAO", "document": "Doc 9859", "criticality": "high"}
            ],
            "distances": [0.15, 0.23, 0.31],
            "confidence": 0.82
        }
    
    def _calculate_rag_confidence(self, results: Dict) -> float:
        """Calcula confidence del RAG basado en distances"""
        distances = results.get('distances', [[]])[0]
        if not distances:
            return 0.5
        
        # Convertir distances a confidence (0-1)
        # Distance baja = alta confidence
        avg_distance = sum(distances[:3]) / min(3, len(distances))
        confidence = max(0, min(1, 1 - avg_distance))
        
        return round(confidence, 2)
    
    def _calculate_compliance(self, rag_results: Dict, context: Dict) -> float:
        """Calcula compliance score (0-100)"""
        score = 100.0
        
        # Penalizaciones por criterios faltantes
        if not context.get('has_supervisor_signature'):
            score -= 15  # EASA Part-66 requirement
        
        if not context.get('has_gps_evidence'):
            score -= 20  # OnTrackIA forensic policy
        
        if not context.get('has_timestamp_valid'):
            score -= 25  # Timestamp requirement
        
        if not context.get('has_photo_evidence'):
            score -= 30  # Visual evidence required
        
        # Ajuste por relevancia RAG
        rag_confidence = rag_results.get('confidence', 0.75)
        if rag_confidence < 0.7:
            score -= 10  # Low normative match
        
        # Bonus por best practices
        if context.get('has_voice_report'):
            score += 5
        
        if context.get('has_multiple_photos'):
            score += 3
        
        return max(0, min(100, round(score, 1)))
    
    def _extract_normative_references(self, rag_results: Dict) -> List[Dict]:
        """Extrae referencias normativas del RAG"""
        references = []
        
        metadatas = rag_results.get('metadatas', [])
        distances = rag_results.get('distances', [])
        
        for i, meta in enumerate(metadatas[:5]):  # Top 5
            relevance = 1 - distances[i] if i < len(distances) else 0.5
            
            # Extraer authority de la categoría
            category = meta.get('category', 'TECHNICAL_DOC')
            category_label = meta.get('category_label', 'Unknown')
            
            # Mapear categoría a authority
            authority_map = {
                'EASA_REGULATION': 'EASA',
                'FAA_REGULATION': 'FAA',
                'ICAO_STANDARD': 'ICAO',
                'UK_CAA_REGULATION': 'UK CAA',
                'LAR_REGULATION': 'LAR',
                'AUDIT_REQUIREMENT': 'OnTrackIA',
                'OJT_STANDARD': 'OnTrackIA OJT'
            }
            
            authority = authority_map.get(category, category_label)
            
            references.append({
                "authority": authority,
                "document": meta.get('file_name', 'Unknown'),
                "section": f"Chunk {meta.get('chunk_index', 0) + 1}/{meta.get('total_chunks', 1)}",
                "relevance": round(relevance, 2),
                "criticality": "high" if relevance > 0.8 else "medium" if relevance > 0.6 else "low"
            })
        
        # Ordenar por relevancia
        references.sort(key=lambda x: x['relevance'], reverse=True)
        
        return references
    
    def _identify_discrepancies(
        self,
        rag_results: Dict,
        context: Dict,
        compliance_score: float
    ) -> List[Dict]:
        """Identifica discrepancias basado en RAG y contexto"""
        discrepancies = []
        
        # Discrepancia: Falta firma supervisor
        if not context.get('has_supervisor_signature'):
            discrepancies.append({
                "severity": "high",
                "description": "Task requires supervisor signature (EASA Part-66 Appendix I)",
                "recommendation": "Add supervisor digital signature before validation",
                "regulation": "EASA Part-66"
            })
        
        # Discrepancia: Sin evidencia GPS
        if not context.get('has_gps_evidence'):
            discrepancies.append({
                "severity": "critical",
                "description": "GPS coordinates missing from visual evidence",
                "recommendation": "Retake photo with GPS enabled",
                "regulation": "OnTrackIA Forensic Policy"
            })
        
        # Discrepancia: Timestamp inválido
        if not context.get('has_timestamp_valid'):
            discrepancies.append({
                "severity": "critical",
                "description": "Timestamp validation failed (>5 minutes old or future)",
                "recommendation": "Capture fresh evidence within 5-minute window",
                "regulation": "OnTrackIA Zero Insurrections"
            })
        
        # Discrepancia detectada por RAG
        if compliance_score < 70:
            # Buscar en documentos RAG
            documents = rag_results.get('documents', [])
            if documents:
                discrepancies.append({
                    "severity": "medium",
                    "description": f"Low compliance with regulatory standards ({compliance_score}%)",
                    "recommendation": "Review task execution against regulatory references",
                    "regulation": "General Compliance"
                })
        
        return discrepancies
    
    def _classify_risk_level(self, compliance_score: float) -> str:
        """Clasifica nivel de riesgo basado en compliance"""
        if compliance_score >= 85:
            return "green"
        elif compliance_score >= 60:
            return "yellow"
        else:
            return "red"
    
    def _generate_insights(self, rag_results: Dict, territory: str = None) -> str:
        """Genera insights en lenguaje natural con contexto territorial"""
        confidence = rag_results.get('confidence', 0.75)
        docs_count = len(rag_results.get('documents', []))
        
        # Contexto territorial
        territory_context = f" for {territory} jurisdiction" if territory else ""
        
        if confidence > 0.8:
            return f"High confidence analysis{territory_context} based on {docs_count} regulatory references. Task execution aligns well with international aviation standards (EASA, FAA, ICAO)."
        elif confidence > 0.6:
            return f"Moderate confidence analysis{territory_context} based on {docs_count} regulatory references. Some aspects require closer review against specific regulatory requirements."
        else:
            return f"Low confidence analysis{territory_context}. Limited regulatory references found ({docs_count}). Manual review recommended."


class AuditAnalysisOrchestrator:
    """
    Orquestador de Agentes Multi-IA
    ================================
    Coordina múltiples agentes especializados
    """
    
    def __init__(self):
        # Inicializar ChromaDB client
        self.chroma_client = self._init_chromadb()
        
        # Registro de agentes activos
        self.agents = {
            "senior_auditor": SeniorAuditorCoachAgent(self.chroma_client)
        }
        
        # Agentes futuros (placeholder)
        self.future_agents = [
            "visual_inspector",    # Computer vision
            "risk_assessor",       # Patrones de error
            "regulatory_monitor",  # Vigilancia normativa
            "voice_analyzer"       # STT avanzado
        ]
    
    def _init_chromadb(self):
        """Inicializa ChromaDB client"""
        if not chromadb:
            print("[Orchestrator] Warning: ChromaDB not installed")
            return None
        
        try:
            # Persistent client
            client = chromadb.PersistentClient(
                path="./data/chromadb",
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            return client
        except Exception as e:
            print(f"[Orchestrator] ChromaDB init error: {e}")
            return None
    
    def analyze_evidence(
        self,
        evidence_id: str,
        task_description: str,
        context: Dict
    ) -> Dict:
        """
        Analiza evidencia usando todos los agentes activos
        
        Args:
            evidence_id: ID de la evidencia visual
            task_description: Descripción de la tarea
            context: Contexto adicional
        
        Returns:
            Análisis consolidado de todos los agentes
        """
        start_time = datetime.now()
        
        # Ejecutar análisis de Senior Auditor Coach
        senior_analysis = self.agents["senior_auditor"].analyze(
            task_description,
            context
        )
        
        # Consolidar resultados (por ahora solo 1 agente)
        # En el futuro, aquí se ejecutarían múltiples agentes
        consolidated = {
            "evidence_id": evidence_id,
            "timestamp": datetime.now().isoformat(),
            "primary_agent": "senior_auditor",
            "compliance_score": senior_analysis["compliance_score"],
            "risk_level": senior_analysis["risk_level"],
            "normative_references": senior_analysis["normative_references"],
            "discrepancies": senior_analysis["discrepancies"],
            "rag_insights": senior_analysis["rag_insights"],
            "agent_details": {
                "senior_auditor": senior_analysis
            },
            "processing_time_ms": int(
                (datetime.now() - start_time).total_seconds() * 1000
            )
        }
        
        return consolidated
    
    def get_active_agents(self) -> List[str]:
        """Lista de agentes activos"""
        return list(self.agents.keys())
    
    def get_future_agents(self) -> List[str]:
        """Lista de agentes futuros (roadmap)"""
        return self.future_agents


# Singleton instance
_orchestrator_instance = None

def get_orchestrator() -> AuditAnalysisOrchestrator:
    """Obtener instancia singleton del orquestador"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AuditAnalysisOrchestrator()
    return _orchestrator_instance


# Testing
if __name__ == "__main__":
    print("="*70)
    print("MULTI-AGENT AUDIT ANALYSIS SYSTEM")
    print("="*70)
    
    orchestrator = get_orchestrator()
    
    print(f"\nActive Agents: {orchestrator.get_active_agents()}")
    print(f"Future Agents: {orchestrator.get_future_agents()}")
    
    # Test analysis
    result = orchestrator.analyze_evidence(
        evidence_id="test_001",
        task_description="Engine Run - CFM56-7B on B737-800",
        context={
            "aircraft_type": "B737-800",
            "component": "CFM56-7B Engine",
            "task_code": "71-00-00",
            "has_supervisor_signature": False,
            "has_gps_evidence": True,
            "has_timestamp_valid": True,
            "has_photo_evidence": True
        }
    )
    
    print("\n" + "="*70)
    print("ANALYSIS RESULT")
    print("="*70)
    print(f"Compliance Score: {result['compliance_score']}%")
    print(f"Risk Level: {result['risk_level'].upper()}")
    print(f"Processing Time: {result['processing_time_ms']}ms")
    print(f"\nDiscrepancies Found: {len(result['discrepancies'])}")
    for disc in result['discrepancies']:
        print(f"  [{disc['severity'].upper()}] {disc['description']}")
    print("="*70 + "\n")
