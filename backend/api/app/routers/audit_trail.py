"""
Audit Trail Router - Master Audit Log Dashboard
Aviation-grade traceability viewer for FAA/EASA/CASA compliance
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models.system_audit_log import SystemAuditLog

router = APIRouter(prefix="/api/v2/audit-trail", tags=["Master Audit Trail"])


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    user_name: str
    action_type: str
    action_description: str
    entity_type: str
    entity_id: str
    changes_summary: str
    ip_address: Optional[str]
    severity: str
    entry_hash: str
    
    class Config:
        from_attributes = True


class AuditLogDetail(BaseModel):
    id: int
    timestamp: datetime
    user_id: int
    user_name: str
    user_email: Optional[str]
    action_type: str
    action_description: str
    entity_type: str
    entity_id: str
    previous_state: Optional[dict]
    new_state: Optional[dict]
    changes_summary: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_info: Optional[dict]
    request_id: Optional[str]
    endpoint: Optional[str]
    http_method: Optional[str]
    entry_hash: str
    previous_hash: Optional[str]
    severity: str
    tags: Optional[dict]
    
    class Config:
        from_attributes = True


class AuditTrailStats(BaseModel):
    total_entries: int
    entries_today: int
    entries_this_week: int
    by_action_type: dict
    by_entity_type: dict
    by_severity: dict
    integrity_status: str


# ==========================================
# ENDPOINTS
# ==========================================

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get Master Audit Trail logs with filters.
    
    Aviation Compliance: FAA/EASA/CASA require complete traceability.
    This endpoint provides the 'Black Box' view of all system operations.
    """
    # TODO: Get tenant_id from JWT auth
    tenant_id = 1
    
    query = db.query(SystemAuditLog).filter(
        SystemAuditLog.tenant_id == tenant_id
    )
    
    # Apply filters
    if start_date:
        query = query.filter(SystemAuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(SystemAuditLog.timestamp <= end_date)
    if user_id:
        query = query.filter(SystemAuditLog.user_id == user_id)
    if action_type:
        query = query.filter(SystemAuditLog.action_type == action_type)
    if entity_type:
        query = query.filter(SystemAuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(SystemAuditLog.entity_id == entity_id)
    if severity:
        query = query.filter(SystemAuditLog.severity == severity)
    
    # Order by timestamp descending (most recent first)
    query = query.order_by(desc(SystemAuditLog.timestamp))
    
    # Pagination
    logs = query.offset(offset).limit(limit).all()
    
    return logs


@router.get("/logs/{log_id}", response_model=AuditLogDetail)
async def get_audit_log_detail(
    log_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed audit log entry with full forensic information"""
    tenant_id = 1
    
    log = db.query(SystemAuditLog).filter(
        SystemAuditLog.id == log_id,
        SystemAuditLog.tenant_id == tenant_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return log


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLogResponse])
async def get_entity_history(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete history of an entity.
    
    Shows all operations performed on a specific audit, finding, RCA, or SMS report.
    Critical for regulatory compliance and forensic investigation.
    """
    tenant_id = 1
    
    logs = db.query(SystemAuditLog).filter(
        SystemAuditLog.tenant_id == tenant_id,
        SystemAuditLog.entity_type == entity_type,
        SystemAuditLog.entity_id == entity_id
    ).order_by(SystemAuditLog.timestamp).all()
    
    return logs


@router.get("/stats", response_model=AuditTrailStats)
async def get_audit_trail_stats(
    db: Session = Depends(get_db)
):
    """Get Master Audit Trail statistics"""
    tenant_id = 1
    
    # Total entries
    total = db.query(SystemAuditLog).filter(
        SystemAuditLog.tenant_id == tenant_id
    ).count()
    
    # Entries today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today = db.query(SystemAuditLog).filter(
        SystemAuditLog.tenant_id == tenant_id,
        SystemAuditLog.timestamp >= today_start
    ).count()
    
    # Entries this week
    week_start = today_start - timedelta(days=today_start.weekday())
    this_week = db.query(SystemAuditLog).filter(
        SystemAuditLog.tenant_id == tenant_id,
        SystemAuditLog.timestamp >= week_start
    ).count()
    
    # By action type
    action_types = {}
    for action in ["CREATE", "UPDATE", "DELETE", "CLOSE", "VALIDATE", "APPROVE"]:
        count = db.query(SystemAuditLog).filter(
            SystemAuditLog.tenant_id == tenant_id,
            SystemAuditLog.action_type == action
        ).count()
        if count > 0:
            action_types[action] = count
    
    # By entity type
    entity_types = {}
    for entity in ["AUDIT_CONTEXT", "FINDING", "RCA", "SMS_REPORT", "AI_ACT_AUDIT"]:
        count = db.query(SystemAuditLog).filter(
            SystemAuditLog.tenant_id == tenant_id,
            SystemAuditLog.entity_type == entity
        ).count()
        if count > 0:
            entity_types[entity] = count
    
    # By severity
    severity_counts = {}
    for severity in ["INFO", "WARNING", "CRITICAL"]:
        count = db.query(SystemAuditLog).filter(
            SystemAuditLog.tenant_id == tenant_id,
            SystemAuditLog.severity == severity
        ).count()
        if count > 0:
            severity_counts[severity] = count
    
    # Verify integrity of last 100 entries
    recent_logs = db.query(SystemAuditLog).filter(
        SystemAuditLog.tenant_id == tenant_id
    ).order_by(desc(SystemAuditLog.id)).limit(100).all()
    
    integrity_ok = all(log.verify_integrity() for log in recent_logs)
    
    return AuditTrailStats(
        total_entries=total,
        entries_today=today,
        entries_this_week=this_week,
        by_action_type=action_types,
        by_entity_type=entity_types,
        by_severity=severity_counts,
        integrity_status="VERIFIED" if integrity_ok else "COMPROMISED"
    )


@router.post("/verify-integrity")
async def verify_audit_trail_integrity(
    start_id: Optional[int] = None,
    end_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Verify blockchain-like integrity of audit trail.
    
    Checks that:
    1. Each entry's hash matches its content
    2. Each entry's previous_hash matches the previous entry's hash
    3. No entries have been tampered with
    
    Critical for forensic evidence admissibility.
    """
    tenant_id = 1
    
    query = db.query(SystemAuditLog).filter(
        SystemAuditLog.tenant_id == tenant_id
    ).order_by(SystemAuditLog.id)
    
    if start_id:
        query = query.filter(SystemAuditLog.id >= start_id)
    if end_id:
        query = query.filter(SystemAuditLog.id <= end_id)
    
    logs = query.all()
    
    if not logs:
        return {
            "success": True,
            "verified_count": 0,
            "message": "No logs to verify"
        }
    
    failed_entries = []
    broken_chain = []
    
    for i, log in enumerate(logs):
        # Verify individual entry hash
        if not log.verify_integrity():
            failed_entries.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "reason": "Hash mismatch"
            })
        
        # Verify chain integrity
        if i > 0:
            expected_previous_hash = logs[i-1].entry_hash
            if log.previous_hash != expected_previous_hash:
                broken_chain.append({
                    "id": log.id,
                    "expected_previous": expected_previous_hash,
                    "actual_previous": log.previous_hash
                })
    
    integrity_ok = len(failed_entries) == 0 and len(broken_chain) == 0
    
    return {
        "success": integrity_ok,
        "verified_count": len(logs),
        "failed_entries": failed_entries,
        "broken_chain": broken_chain,
        "status": "VERIFIED" if integrity_ok else "COMPROMISED",
        "message": "Audit trail integrity verified" if integrity_ok else "Integrity violations detected"
    }


@router.get("/export")
async def export_audit_trail(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    """
    Export audit trail for regulatory compliance.
    
    Required for FAA/EASA audits and legal proceedings.
    """
    tenant_id = 1
    
    query = db.query(SystemAuditLog).filter(
        SystemAuditLog.tenant_id == tenant_id
    )
    
    if start_date:
        query = query.filter(SystemAuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(SystemAuditLog.timestamp <= end_date)
    
    logs = query.order_by(SystemAuditLog.timestamp).all()
    
    if format == "csv":
        # TODO: Implement CSV export
        raise HTTPException(status_code=501, detail="CSV export not yet implemented")
    
    return {
        "success": True,
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "user": log.user_name,
                "action": log.action_type,
                "entity": f"{log.entity_type}/{log.entity_id}",
                "hash": log.entry_hash
            }
            for log in logs
        ]
    }
