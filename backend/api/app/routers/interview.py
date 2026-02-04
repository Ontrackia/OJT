#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Interview Endpoint
========================================
Endpoint para procesar entrevistas críticas y generar tokens forenses

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional
import hashlib
import json
from datetime import datetime

from app.models.ojt_models import OJTPersonTask, OJTTask
from app.services.ai_guardian import AIGuardianService
from app.database import get_db

router = APIRouter()

class InterviewAnswersRequest(BaseModel):
    user_id: int
    task_id: str
    answers: Dict[str, Dict[str, str]]
    language: str = 'es'

class InterviewCompletionResponse(BaseModel):
    interview_token: str
    is_approved: bool
    message: str

@router.post("/interview/complete", response_model=InterviewCompletionResponse)
async def complete_critical_interview(
    request: InterviewAnswersRequest,
    db: Session = Depends(get_db)
):
    """
    Procesa las respuestas de una entrevista crítica y genera token forense
    
    Args:
        request: Respuestas de la entrevista
        db: Sesión de base de datos
    
    Returns:
        Token SHA-256 y aprobación
    """
    # Buscar la tarea de la persona
    person_task = db.query(OJTPerson Task).filter_by(
        task_id=request.task_id
    ).first()
    
    if not person_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verificar que la tarea sea crítica
    task = db.query(OJTTask).filter_by(id=request.task_id).first()
    if not task or not task.is_critical:
        raise HTTPException(status_code=400, detail="Task is not critical")
    
    # Generar sello forense de la entrevista
    audit_data = {
        "user_id": request.user_id,
        "task_id": request.task_id,
        "answers": request.answers,
        "timestamp": datetime.utcnow().isoformat(),
        "language": request.language
    }
    
    # Calcular hash SHA-256
    audit_json = json.dumps(audit_data, sort_keys=True)
    interview_token = hashlib.sha256(audit_json.encode('utf-8')).hexdigest()
    
    # Guardar en la base de datos
    person_task.audit_log = audit_json
    person_task.interview_completed = True
    person_task.interview_token = interview_token
    
    db.commit()
    
    # Mensaje de respuesta
    message = (
        f"Entrevista completada y sellada. Token: {interview_token[:16]}..." 
        if request.language == 'es' else
        f"Interview completed and sealed. Token: {interview_token[:16]}..."
    )
    
    return InterviewCompletionResponse(
        interview_token=interview_token,
        is_approved=True,
        message=message
    )

@router.post("/task/validate")
async def validate_task_with_guard(
    task_id: str,
    report_text: str,
    gps_coords: Optional[Dict[str, float]],
    evidence_hash: Optional[str],
    language: str = 'es',
    db: Session = Depends(get_db)
):
    """
    Valida una tarea con el guardia IA antes de marcarla como validated
    
    Args:
        task_id: ID de la tarea
        report_text: Texto del reporte técnico
        gps_coords: Coordenadas GPS
        evidence_hash: Hash SHA-256 de evidencia
        language: Idioma (es/en)
        db: Sesión de base de datos
    
    Returns:
        Resultado de validación
    """
    # Buscar tarea
    person_task = db.query(OJTPersonTask).filter_by(task_id=task_id).first()
    if not person_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verificar si es crítica y requiere entrevista
    task = db.query(OJTTask).filter_by(id=task_id).first()
    if task.is_critical and not person_task.interview_completed:
        raise HTTPException(
            status_code=400, 
            detail="Critical task requires interview completion before validation" 
                if language == 'en' else 
                "Tarea crítica requiere completar entrevista antes de validar"
        )
    
    # Usar guardia IA
    guardian = AIGuardianService(language=language)
    result = guardian.validate_task_report(
        report_text=report_text,
        gps_coords=gps_coords,
        evidence_hash=evidence_hash,
        task_code=task.task_code
    )
    
    if not result.is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "message": result.recommendation,
                "errors": result.errors,
                "warnings": result.warnings,
                "score": result.score
            }
        )
    
    # Validación exitosa
    person_task.status = 'validated'
    person_task.validated_at = datetime.utcnow()
    person_task.notes = f"{person_task.notes or ''}\n\n[AI Guardian Score: {result.score}/100]"
    
    db.commit()
    
    return {
        "status": "validated",
        "score": result.score,
        "message": result.recommendation
    }
