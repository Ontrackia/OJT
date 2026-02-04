"""
SMS Quick Report - Just Culture Voluntary Reporting
Accessible from login page without authentication
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import hashlib

from app.database import get_db
from app.models.sms_models import SMSReport
from app.services.evidence_service import EvidenceService

router = APIRouter(prefix="/api/v2/sms-quick", tags=["SMS Quick Report"])


@router.post("/report")
async def create_quick_report(
    description: str = Form(...),
    notifier_name: Optional[str] = Form(None),
    notifier_contact: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    severity: str = Form("MEDIUM"),
    ip_address: str = Form(...),
    evidences: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create SMS voluntary report without authentication.
    
    Just Culture principles:
    - No login required
    - Anonymous option (no notifier info)
    - IP hashed for privacy
    - Immediate submission
    """
    
    # Hash IP for privacy (not storing real IP)
    ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
    
    # Create SMS report
    sms_report = SMSReport(
        organization_id=1,  # Default organization for anonymous reports
        report_type="VOLUNTARY_CONFIDENTIAL",
        description=description,
        reported_by_name=notifier_name or "Anonymous",
        reported_by_email=notifier_contact if notifier_contact and "@" in notifier_contact else None,
        reported_by_phone=notifier_contact if notifier_contact and "@" not in notifier_contact else None,
        location=location,
        severity=severity,
        status="SUBMITTED",
        is_anonymous=notifier_name is None,
        ip_hash=ip_hash,
        submitted_at=datetime.utcnow()
    )
    
    db.add(sms_report)
    db.flush()
    
    # Upload evidences if provided
    if evidences:
        evidence_service = EvidenceService(db, organization_id=1)
        
        for evidence_file in evidences:
            try:
                evidence_service.upload_evidence(
                    file=evidence_file.file,
                    filename=evidence_file.filename,
                    entity_type="SMS_REPORT",
                    entity_id=sms_report.report_id,
                    uploaded_by=0,  # Anonymous
                    uploaded_by_name="Anonymous Reporter",
                    description="Voluntary SMS report evidence"
                )
            except Exception as e:
                print(f"⚠️ Evidence upload failed: {str(e)}")
                # Don't fail the report if evidence upload fails
    
    db.commit()
    db.refresh(sms_report)
    
    return {
        "success": True,
        "report_id": sms_report.report_id,
        "message": "Reporte recibido. Gracias por contribuir a la seguridad.",
        "message_en": "Report received. Thank you for contributing to safety."
    }
