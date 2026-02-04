"""
OJT Router
Endpoints for On-the-Job Training tracking
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.middleware.jwt_auth import get_current_user
from app.dependencies import require_permission
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.ojt_models import OJTPerson, OJTTask, OJTPersonTask, OJTEvidence
from app.mongodb_config import store_evidence
from app.services.pdf_chunking import PDFChunker
from app.services.audit_logging import log_request_action
from datetime import datetime, date
import os

router = APIRouter(prefix="/api/ojt", tags=["OJT - Training"])

# Request/Response models
class PersonCreate(BaseModel):
    full_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    supervisor_id: Optional[int] = None

class TaskCreate(BaseModel):
    task_code: str
    task_title: str
    task_description: Optional[str] = None
    task_category: Optional[str] = None
    requires_evidence: bool = True

class PersonTaskAssign(BaseModel):
    person_id: str
    task_id: str
    target_completion_date: Optional[str] = None

class ProgressResponse(BaseModel):
    person_id: str
    person_name: str
    total_tasks: int
    completed_tasks: int
    validated_tasks: int
    progress_percentage: float
    pending_validation: int

# ==========================================
# PERSONS
# ==========================================

@router.post("/persons")
async def create_person(
    person: PersonCreate,
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission("ojt.manage.definitions")),
    db: Session = Depends(get_db)
):
    """Create OJT person"""
    new_person = OJTPerson(
        tenant_id=current_user['tenant_id'],
        user_id=current_user['id'],  # Link to user
        full_name=person.full_name,
        position=person.position,
        department=person.department,
        supervisor_id=person.supervisor_id
    )
    
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    
    return {"id": new_person.id, "name": new_person.full_name}

# ==========================================
# TASKS
# ==========================================

@router.post("/tasks")
async def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission("ojt.manage.definitions")),
    db: Session = Depends(get_db)
):
    """Create OJT task"""
    new_task = OJTTask(
        tenant_id=current_user['tenant_id'],
        task_code=task.task_code,
        task_title=task.task_title,
        task_description=task.task_description,
        task_category=task.task_category,
        requires_evidence=task.requires_evidence,
        created_by=current_user['id']
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {"id": new_task.id, "code": new_task.task_code}

@router.post("/assign")
async def assign_task(
    assignment: PersonTaskAssign,
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission("ojt.manage.definitions")),
    db: Session = Depends(get_db),
    request = None
):
    """Assign task to person"""
    target_date = None
    if assignment.target_completion_date:
        target_date = date.fromisoformat(assignment.target_completion_date)
    
    person_task = OJTPersonTask(
        tenant_id=current_user['tenant_id'],
        person_id=assignment.person_id,
        task_id=assignment.task_id,
        target_completion_date=target_date,
        status='assigned'
    )
    
    db.add(person_task)
    db.commit()
    db.refresh(person_task)
    
    # Log action
    log_request_action(
        db=db,
        current_user=current_user,
        action_type="create",
        module="ojt",
        entity_type="assignment",
        entity_id=person_task.id,
        request=request
    )
    
    return {"id": person_task.id, "status": "assigned"}

# ==========================================
# PROGRESS DASHBOARD
# ==========================================

@router.get("/progress/{person_id}", response_model=ProgressResponse)
async def get_person_progress(
    person_id: str,
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission("ojt.read.user_progress")),
    db: Session = Depends(get_db)
):
    """Get training progress for person"""
    person = db.query(OJTPerson).filter(
        OJTPerson.id == person_id,
        OJTPerson.tenant_id == current_user['tenant_id']
    ).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Get all tasks
    tasks = db.query(OJTPersonTask).filter(
        OJTPersonTask.person_id == person_id,
        OJTPersonTask.tenant_id == current_user['tenant_id']
    ).all()
    
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == 'completed')
    validated = sum(1 for t in tasks if t.supervisor_validated)
    pending_validation = sum(1 for t in tasks if t.status == 'completed' and not t.supervisor_validated)
    
    progress = (validated / total * 100) if total > 0 else 0
    
    return ProgressResponse(
        person_id=person.id,
        person_name=person.full_name,
        total_tasks=total,
        completed_tasks=completed,
        validated_tasks=validated,
        progress_percentage=round(progress, 2),
        pending_validation=pending_validation
    )

# ==========================================
# EVIDENCES
# ==========================================

@router.post("/evidences/{person_task_id}")
async def upload_evidence(
    person_task_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission("ojt.create.evidence")),
    db: Session = Depends(get_db),
    request = None
):
    """Upload evidence for task"""
    # Get person task
    person_task = db.query(OJTPersonTask).filter(
        OJTPersonTask.id == person_task_id,
        OJTPersonTask.tenant_id == current_user['tenant_id']
    ).first()
    
    if not person_task:
        raise HTTPException(status_code=404, detail="Task assignment not found")
    
    # Save file temporarily
    upload_dir = f"/tmp/ojt_evidences/{current_user['tenant_id']}"
    os.makedirs(upload_dir, exist_ok=True)
    
    import uuid
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Calculate hash
    file_hash = PDFChunker.calculate_file_hash(file_path)
    
    # Store in MongoDB
    mongo_id = store_evidence(
        tenant_id=current_user['tenant_id'],
        entity_type="ojt_evidence",
        entity_id=person_task_id,
        file_name=file.filename,
        file_data=content,
        file_type=file.content_type or "application/octet-stream",
        file_hash=file_hash,
        uploaded_by=current_user['id']
    )
    
    # Create evidence record
    evidence = OJTEvidence(
        tenant_id=current_user['tenant_id'],
        person_task_id=person_task_id,
        evidence_type="photo" if "image" in (file.content_type or "") else "document",
        file_path=mongo_id,  # MongoDB ID
        file_hash_sha256=file_hash,
        uploaded_by=current_user['id'],
        description=description
    )
    
    db.add(evidence)
    
    # Update task status if not already completed
    if person_task.status == 'assigned':
        person_task.status = 'in_progress'
    
    db.commit()
    
    # Log action
    log_request_action(
        db=db,
        current_user=current_user,
        action_type="create",
        module="ojt",
        entity_type="evidence",
        entity_id=evidence.id,
        request=request
    )
    
    return {"success": True, "evidence_id": evidence.id}

# ==========================================
# SUPERVISOR VALIDATION
# ==========================================

@router.post("/validate/{person_task_id}")
async def validate_task(
    person_task_id: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission("ojt.approve.task")),
    db: Session = Depends(get_db),
    request = None
):
    """
    Validate task completion (SUPERVISOR ONLY)
    
    Rules:
    - Only supervisor can validate
    - Evidence must be uploaded
    - Task must be completed
    """
    person_task = db.query(OJTPersonTask).filter(
        OJTPersonTask.id == person_task_id,
        OJTPersonTask.tenant_id == current_user['tenant_id']
    ).first()
    
    if not person_task:
        raise HTTPException(status_code=404, detail="Task assignment not found")
    
    # Check if user is supervisor
    person = db.query(OJTPerson).filter(
        OJTPerson.id == person_task.person_id
    ).first()
    
    if person.supervisor_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Only supervisor can validate")
    
    # Check if evidence exists
    evidence_count = db.query(OJTEvidence).filter(
        OJTEvidence.person_task_id == person_task_id
    ).count()
    
    if evidence_count == 0:
        raise HTTPException(status_code=400, detail="Evidence required before validation")
    
    # Validate task
    person_task.status = 'validated'
    person_task.supervisor_validated = True
    person_task.validated_by = current_user['id']
    person_task.validated_at = datetime.utcnow()
    person_task.actual_completion_date = date.today()
    if notes:
        person_task.notes = notes
    
    db.commit()
    
    # Log action
    log_request_action(
        db=db,
        current_user=current_user,
        action_type="validate",
        module="ojt",
        entity_type="task",
        entity_id=person_task.id,
        request=request
    )
    
    return {"success": True, "status": "validated"}

@router.get("/check-authorization/{person_id}")
async def check_authorization_eligibility(
    person_id: str,
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission("ojt.read.user_progress")),
    db: Session = Depends(get_db)
):
    """
    Check if person is eligible for authorization
    
    Rules:
    - All assigned tasks must be validated
    - OJT must be 100% complete
    """
    tasks = db.query(OJTPersonTask).filter(
        OJTPersonTask.person_id == person_id,
        OJTPersonTask.tenant_id == current_user['tenant_id']
    ).all()
    
    total = len(tasks)
    validated = sum(1 for t in tasks if t.supervisor_validated)
    
    eligible = (total > 0 and validated == total)
    
    return {
        "eligible": eligible,
        "total_tasks": total,
        "validated_tasks": validated,
        "pending_tasks": total - validated,
        "message": "Eligible for authorization" if eligible else "OJT incomplete - cannot issue authorization"
    }
