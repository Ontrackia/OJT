"""
SMS Router - PostgreSQL Backend
Endpoints for Safety Management System reports with ICAO 5x5 risk matrix
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.services.sms_service import SMSService

router = APIRouter(prefix="/api/v2/sms", tags=["SMS PostgreSQL"])


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class SMSReportCreate(BaseModel):
    report_id: str
    territory: str
    event_description: str
    severity: int  # 1-5 (ICAO)
    probability: int  # 1-5 (ICAO)
    inherited_audit_id: Optional[str] = None
    inherited_scope: Optional[dict] = None
    metadata: Optional[dict] = None


# ==========================================
# SMS REPORTS
# ==========================================

@router.post("/reports")
async def create_sms_report(
    data: SMSReportCreate,
    db: Session = Depends(get_db)
):
    """Create SMS safety report with automatic risk calculation"""
    # TODO: Get from JWT auth
    organization_id = 1
    user_id = 1
    
    service = SMSService(db, organization_id)
    
    try:
        report = service.create_sms_report(
            report_id=data.report_id,
            territory=data.territory,
            event_description=data.event_description,
            severity=data.severity,
            probability=data.probability,
            created_by=user_id,
            inherited_audit_id=data.inherited_audit_id,
            inherited_scope=data.inherited_scope,
            metadata=data.metadata
        )
        
        return {
            "success": True,
            "report_id": report.report_id,
            "risk_score": report.risk_score,
            "risk_level": report.risk_level,
            "report_hash": report.report_hash,
            "created_at": report.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def list_sms_reports(
    territory: Optional[str] = None,
    risk_level: Optional[str] = None,
    audit_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List SMS reports with filters"""
    organization_id = 1
    service = SMSService(db, organization_id)
    
    reports = service.list_sms_reports(
        territory=territory,
        risk_level=risk_level,
        audit_id=audit_id,
        limit=limit
    )
    
    return {
        "success": True,
        "count": len(reports),
        "reports": [
            {
                "report_id": r.report_id,
                "territory": r.territory,
                "event_description": r.event_description,
                "severity": r.severity,
                "probability": r.probability,
                "risk_score": r.risk_score,
                "risk_level": r.risk_level,
                "report_hash": r.report_hash,
                "inherited_audit_id": r.inherited_audit_id,
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]
    }


@router.get("/reports/{report_id}")
async def get_sms_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """Get SMS report details"""
    organization_id = 1
    service = SMSService(db, organization_id)
    
    report = service.get_sms_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="SMS Report not found")
    
    return {
        "success": True,
        "report": {
            "report_id": report.report_id,
            "territory": report.territory,
            "event_description": report.event_description,
            "severity": report.severity,
            "probability": report.probability,
            "risk_score": report.risk_score,
            "risk_level": report.risk_level,
            "report_hash": report.report_hash,
            "inherited_audit_id": report.inherited_audit_id,
            "inherited_scope": report.inherited_scope,
            "metadata": report.metadata,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat() if report.updated_at else None
        }
    }


# ==========================================
# RISK MATRIX
# ==========================================

@router.get("/risk-matrix")
async def get_risk_matrix(
    matrix_type: str = "ICAO_5x5",
    db: Session = Depends(get_db)
):
    """Get ICAO 5x5 risk matrix"""
    organization_id = 1
    service = SMSService(db, organization_id)
    
    matrix = service.get_risk_matrix(matrix_type)
    
    return {
        "success": True,
        "matrix": matrix
    }


@router.post("/calculate-risk")
async def calculate_risk(
    severity: int,
    probability: int,
    db: Session = Depends(get_db)
):
    """Calculate risk level from severity and probability"""
    organization_id = 1
    service = SMSService(db, organization_id)
    
    if not (1 <= severity <= 5 and 1 <= probability <= 5):
        raise HTTPException(
            status_code=400,
            detail="Severity and probability must be between 1 and 5"
        )
    
    risk = service.calculate_risk(severity, probability)
    
    return {
        "success": True,
        **risk
    }


# ==========================================
# STATISTICS
# ==========================================

@router.get("/stats")
async def get_sms_stats(
    territory: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get SMS statistics"""
    organization_id = 1
    service = SMSService(db, organization_id)
    
    stats = service.get_sms_stats(territory)
    
    return {
        "success": True,
        **stats
    }
