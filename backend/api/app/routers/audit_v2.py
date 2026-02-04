#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Audit Router V2
=====================================
Endpoints para Dashboard Auditor con integración RAG multi-agente

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Optional, List
import json
from datetime import datetime
import sys

# Importar servicio multi-agente
sys.path.append(str(Path(__file__).parent.parent.parent / 'services'))
from audit_analysis_service import get_orchestrator

router = APIRouter(prefix="/api/v2/audit", tags=["Audit V2"])

# Directorio de evidencias
VISUAL_SCANS_DIR = Path("./uploads/visual_scans")
VISUAL_SCANS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/evidences")
async def get_evidences(
    risk_level: Optional[str] = None,
    task_id: Optional[str] = None,
    technician_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50
):
    """
    Lista evidencias visuales con metadata forense
    
    Query Params:
        risk_level: red | yellow | green | all
        task_id: Filter by task
        technician_id: Filter by technician
        date_from, date_to: Date range (ISO format)
        limit: Max results (default 50)
    
    Returns:
        Lista de evidencias con thumbnails y metadata
    """
    try:
        evidences = []
        
        # Buscar archivos WebP en directorio
        webp_files = list(VISUAL_SCANS_DIR.glob("*.webp"))
        
        # Excluir thumbnails
        full_images = [f for f in webp_files if '_thumb' not in f.name]
        
        for img_path in full_images[:limit]:
            # Buscar metadata JSON
            meta_path = img_path.with_suffix('.json')
            
            if meta_path.exists():
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
                
                # Buscar thumbnail
                thumb_name = img_path.stem + '_thumb.webp'
                thumb_path = img_path.parent / thumb_name
                
                # Extraer info básica
                evidence_data = {
                    "id": img_path.stem,
                    "task_id": metadata.get('task_id', 'unknown'),
                    "thumbnail_path": f"/uploads/visual_scans/{thumb_path.name}" if thumb_path.exists() else None,
                    "full_image_path": f"/uploads/visual_scans/{img_path.name}",
                    "metadata": {
                        "gps_latitude": metadata.get('gps_latitude'),
                        "gps_longitude": metadata.get('gps_longitude'),
                        "capture_timestamp": metadata.get('capture_timestamp'),
                        "server_hash": metadata.get('server_hash', metadata.get('photo_hash')),
                        "device_info": metadata.get('device_info', {})
                    },
                    "optimization": metadata.get('optimization', {}),
                    "risk_level": metadata.get('risk_level', 'yellow'),  # Default amarillo
                    "technician_name": metadata.get('technician_name', 'Unknown'),
                    "created_at": metadata.get('capture_timestamp', datetime.now().isoformat())
                }
                
                # Aplicar filtros
                if risk_level and risk_level != 'all':
                    if evidence_data['risk_level'] != risk_level:
                        continue
                
                if task_id and evidence_data['task_id'] != task_id:
                    continue
                
                evidences.append(evidence_data)
        
        # Ordenar por fecha (más recientes primero)
        evidences.sort(
            key=lambda x: x['created_at'],
            reverse=True
        )
        
        return {
            "success": True,
            "count": len(evidences),
            "evidences": evidences
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching evidences: {str(e)}"
        )

@router.post("/analyze")
async def analyze_evidence(
    evidence_id: str,
    task_description: str,
    territory: Optional[str] = None,
    context: dict = None
):
    """
    Analiza evidencia usando sistema multi-agente RAG
    
    Request Body:
        {
            "evidence_id": "visual_scan_1738665015",
            "task_description": "Engine Run - CFM56-7B",
            "territory": "BRAZIL" | "CANADA" | "GLOBAL" | null,
            "context": {
                "aircraft_type": "B737-800",
                "component": "CFM56-7B Engine",
                "task_code": "71-00-00",
                "has_supervisor_signature": false,
                "has_gps_evidence": true,
                "has_timestamp_valid": true,
                "has_photo_evidence": true
            }
        }
    
    Returns:
        Análisis multi-agente con compliance score, referencias normativas, 
        discrepancias y nivel de riesgo
    """
    try:
        # Verificar que evidencia existe
        evidence_path = VISUAL_SCANS_DIR / f"{evidence_id}.webp"
        meta_path = VISUAL_SCANS_DIR / f"{evidence_id}.json"
        
        if not evidence_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Evidence {evidence_id} not found"
            )
        
        # Cargar metadata existente
        existing_metadata = {}
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                existing_metadata = json.load(f)
        
        # Enriquecer contexto con metadata forense
        enriched_context = context or {}
        enriched_context.update({
            "has_gps_evidence": bool(existing_metadata.get('gps_latitude')),
            "has_timestamp_valid": _validate_timestamp(
                existing_metadata.get('capture_timestamp')
            ),
            "has_photo_evidence": True,  # Obvio, tenemos la foto
            "has_supervisor_signature": enriched_context.get(
                'has_supervisor_signature',
                False
            )
        })
        
        # Obtener orquestador multi-agente
        orchestrator = get_orchestrator()
        
        # Ejecutar análisis (con filtro territorial)
        analysis = orchestrator.analyze_evidence(
            evidence_id=evidence_id,
            task_description=task_description,
            context=enriched_context,
            territory=territory  # Filtro territorial para RAG
        )
        
        # Actualizar metadata con resultado del análisis
        existing_metadata['last_analysis'] = {
            "timestamp": analysis['timestamp'],
            "compliance_score": analysis['compliance_score'],
            "risk_level": analysis['risk_level'],
            "territory": territory or "GLOBAL"
        }
        
        # Guardar metadata actualizada
        with open(meta_path, 'w') as f:
            json.dump(existing_metadata, f, indent=2)
        
        return {
            "success": True,
            **analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis error: {str(e)}"
        )

@router.get("/agents")
async def get_active_agents():
    """
    Lista agentes activos y futuros del sistema multi-agente
    
    Returns:
        Información sobre agentes disponibles
    """
    try:
        orchestrator = get_orchestrator()
        
        return {
            "success": True,
            "active_agents": orchestrator.get_active_agents(),
            "future_agents": orchestrator.get_future_agents(),
            "system_info": {
                "orchestrator_version": "2.0",
                "rag_enabled": orchestrator.chroma_client is not None
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/stats")
async def get_audit_stats():
    """
    Estadísticas del dashboard auditor
    
    Returns:
        Métricas agregadas de auditorías
    """
    try:
        # Contar evidencias
        webp_files = list(VISUAL_SCANS_DIR.glob("*.webp"))
        full_images = [f for f in webp_files if '_thumb' not in f.name]
        
        # Contar por nivel de riesgo
        risk_counts = {"red": 0, "yellow": 0, "green": 0}
        
        for img_path in full_images:
            meta_path = img_path.with_suffix('.json')
            if meta_path.exists():
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
                
                risk_level = metadata.get('risk_level', 'yellow')
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        return {
            "success": True,
            "total_evidences": len(full_images),
            "risk_distribution": risk_counts,
            "avg_compliance_score": 75.0,  # TODO: Calcular promedio real
            "last_updated": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

def _validate_timestamp(timestamp_str: Optional[str]) -> bool:
    """Valida que timestamp esté dentro de ventana aceptable"""
    if not timestamp_str:
        return False
    
    try:
        capture_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = (now - capture_time).total_seconds()
        
        # Timestamp válido si < 5 minutos y no futuro
        return 0 <= diff <= 300
    except:
        return False
