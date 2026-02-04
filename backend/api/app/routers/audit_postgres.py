"""
Audit Router - PostgreSQL Backend
Endpoints for audit contexts, findings, and RCA with full persistence
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.services.audit_service import AuditService
from app.models.audit_models import AuditContext, Finding, RCARecord

router = APIRouter(prefix="/api/v2/audit", tags=["Audit PostgreSQL"])


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class AuditContextCreate(BaseModel):
    audit_id: str
    territory: str
    regulation: str
    scope: dict
    
class ComponentCreate(BaseModel):
    component_id: str
    component_type: str
    description: str
    metadata: Optional[dict] = None

class FindingCreate(BaseModel):
    finding_id: str
    component_id: str
    level: int
    description: str
    regulation_reference: str
    severity: Optional[str] = "medium"
    evidence: Optional[dict] = None

class RCACreate(BaseModel):
    rca_id: str
    finding_id: str
    root_cause: str
    corrective_action: str
    preventive_action: Optional[str] = None
    ai_assisted: bool = False
    ai_suggestion: Optional[str] = None


# ==========================================
# AUDIT CONTEXTS
# ==========================================

@router.post("/contexts")
async def create_audit_context(
    data: AuditContextCreate,
    db: Session = Depends(get_db)
):
    """Create new audit context"""
    # TODO: Get from JWT auth
    organization_id = 1
    user_id = 1
    
    service = AuditService(db, organization_id)
    
    try:
        audit = service.create_audit_context(
            audit_id=data.audit_id,
            territory=data.territory,
            regulation=data.regulation,
            scope=data.scope,
            created_by=user_id
        )
        
        return {
            "success": True,
            "audit_id": audit.audit_id,
            "scope_hash": audit.scope_hash,
            "created_at": audit.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contexts")
async def list_audit_contexts(
    territory: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List audit contexts"""
    organization_id = 1
    service = AuditService(db, organization_id)
    
    audits = service.list_audit_contexts(
        territory=territory,
        status=status,
        limit=limit
    )
    
    return {
        "success": True,
        "count": len(audits),
        "audits": [
            {
                "audit_id": a.audit_id,
                "territory": a.territory,
                "regulation": a.regulation,
                "status": a.status,
                "scope": a.scope,
                "scope_hash": a.scope_hash,
                "created_at": a.created_at.isoformat()
            }
            for a in audits
        ]
    }


@router.get("/contexts/{audit_id}")
async def get_audit_context(
    audit_id: str,
    db: Session = Depends(get_db)
):
    """Get audit context details"""
    organization_id = 1
    service = AuditService(db, organization_id)
    
    audit = service.get_audit_context(audit_id)
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return {
        "success": True,
        "audit": {
            "audit_id": audit.audit_id,
            "territory": audit.territory,
            "regulation": audit.regulation,
            "status": audit.status,
            "scope": audit.scope,
            "scope_hash": audit.scope_hash,
            "created_at": audit.created_at.isoformat(),
            "updated_at": audit.updated_at.isoformat() if audit.updated_at else None
        }
    }


# ==========================================
# COMPONENTS
# ==========================================

@router.post("/contexts/{audit_id}/components")
async def create_component(
    audit_id: str,
    data: ComponentCreate,
    db: Session = Depends(get_db)
):
    """Create component linked to audit"""
    organization_id = 1
    user_id = 1
    
    service = AuditService(db, organization_id)
    
    try:
        component = service.create_component(
            audit_id=audit_id,
            component_id=data.component_id,
            component_type=data.component_type,
            description=data.description,
            created_by=user_id,
            metadata=data.metadata
        )
        
        return {
            "success": True,
            "component_id": component.component_id,
            "inherited_scope": component.inherited_scope,
            "created_at": component.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# FINDINGS
# ==========================================

@router.post("/findings")
async def create_finding(
    data: FindingCreate,
    db: Session = Depends(get_db)
):
    """Create finding linked to component"""
    organization_id = 1
    user_id = 1
    
    service = AuditService(db, organization_id)
    
    try:
        finding = service.create_finding(
            finding_id=data.finding_id,
            component_id=data.component_id,
            level=data.level,
            description=data.description,
            regulation_reference=data.regulation_reference,
            created_by=user_id,
            severity=data.severity,
            evidence=data.evidence
        )
        
        return {
            "success": True,
            "finding_id": finding.finding_id,
            "level": finding.level,
            "severity": finding.severity,
            "inherited_audit_id": finding.inherited_audit_id,
            "created_at": finding.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/findings")
async def list_findings(
    audit_id: Optional[str] = None,
    component_id: Optional[str] = None,
    level: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List findings with filters"""
    organization_id = 1
    service = AuditService(db, organization_id)
    
    findings = service.list_findings(
        audit_id=audit_id,
        component_id=component_id,
        level=level,
        limit=limit
    )
    
    return {
        "success": True,
        "count": len(findings),
        "findings": [
            {
                "finding_id": f.finding_id,
                "level": f.level,
                "description": f.description,
                "severity": f.severity,
                "regulation_reference": f.regulation_reference,
                "inherited_audit_id": f.inherited_audit_id,
                "evidence": f.evidence,
                "created_at": f.created_at.isoformat()
            }
            for f in findings
        ]
    }


# ==========================================
# ROOT CAUSE ANALYSIS
# ==========================================

@router.post("/rca")
async def create_rca(
    data: RCACreate,
    db: Session = Depends(get_db)
):
    """Create RCA record linked to finding"""
    organization_id = 1
    user_id = 1
    
    service = AuditService(db, organization_id)
    
    try:
        rca = service.create_rca(
            rca_id=data.rca_id,
            finding_id=data.finding_id,
            root_cause=data.root_cause,
            corrective_action=data.corrective_action,
            created_by=user_id,
            preventive_action=data.preventive_action,
            ai_assisted=data.ai_assisted,
            ai_suggestion=data.ai_suggestion
        )
        
        return {
            "success": True,
            "rca_id": rca.rca_id,
            "root_cause": rca.root_cause,
            "ai_assisted": rca.ai_assisted,
            "inherited_audit_id": rca.inherited_audit_id,
            "created_at": rca.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rca")
async def list_rcas(
    audit_id: Optional[str] = None,
    finding_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List RCA records with filters"""
    organization_id = 1
    service = AuditService(db, organization_id)
    
    rcas = service.list_rcas(
        audit_id=audit_id,
        finding_id=finding_id,
        limit=limit
    )
    
    return {
        "success": True,
        "count": len(rcas),
        "rcas": [
            {
                "rca_id": r.rca_id,
                "root_cause": r.root_cause,
                "corrective_action": r.corrective_action,
                "preventive_action": r.preventive_action,
                "ai_assisted": r.ai_assisted,
                "inherited_audit_id": r.inherited_audit_id,
                "created_at": r.created_at.isoformat()
            }
            for r in rcas
        ]
    }


# ==========================================
# AUDIT TRAIL
# ==========================================

@router.get("/trail")
async def get_audit_trail(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get immutable audit trail"""
    organization_id = 1
    service = AuditService(db, organization_id)
    
    trail = service.get_audit_trail(
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit
    )
    
    return {
        "success": True,
        "count": len(trail),
        "trail": [
            {
                "entity_type": t.entity_type,
                "entity_id": t.entity_id,
                "action": t.action,
                "user_id": t.user_id,
                "data": t.data,
                "entry_hash": t.entry_hash,
                "previous_hash": t.previous_hash,
                "created_at": t.created_at.isoformat()
            }
            for t in trail
        ]
    }
