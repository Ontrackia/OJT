"""
PDF Router for OnTrackIA OJT V2.0
Endpoints for generating and downloading audit PDFs
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/pdf", tags=["PDF Generation"])


@router.get("/audit/{audit_id}")
async def generate_audit_pdf(audit_id: str):
    """
    Generate and download audit report PDF with forensic SHA-256 seal
    
    Args:
        audit_id: Audit context ID (e.g., AUD-XXXXX)
    
    Returns:
        PDF file with forensic integrity seal
    """
    try:
        from app.services.pdf_generator import PDFGenerator
        
        # TODO: Replace with actual database queries when PostgreSQL is migrated
        # For now, using mock data
        
        findings = [
            {
                "finding_id": "F-001",
                "level": 1,
                "title": "Falta certificación técnico",
                "status": "OPEN",
                "deadline": "2026-02-10"
            },
            {
                "finding_id": "F-002",
                "level": 2,
                "title": "Procedimiento desactualizado",
                "status": "OPEN",
                "deadline": "2026-02-15"
            }
        ]
        
        rca_records = [
            {
                "rca_id": "RCA-001",
                "root_cause": "Falta de proceso de verificación de certificaciones",
                "corrective_action": "Implementar checklist automatizado de certificaciones"
            }
        ]
        
        sms_reports = [
            {
                "report_id": "SMS-001",
                "risk_level": "HIGH",
                "status": "OPEN",
                "description": "Técnico operando sin certificación vigente"
            }
        ]
        
        generator = PDFGenerator()
        pdf_bytes = generator.generate_audit_report(
            audit_id=audit_id,
            audit_name="Auditoría Mensual - Febrero 2026",
            regulation="EASA Part-145",
            territory="GLOBAL",
            findings=findings,
            rca_records=rca_records,
            sms_reports=sms_reports
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=audit_{audit_id}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF for audit {audit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.get("/sms/{report_id}")
async def generate_sms_pdf(report_id: str):
    """
    Generate and download SMS report PDF
    
    Args:
        report_id: SMS report ID (e.g., SMS-XXXXX)
    
    Returns:
        PDF file with SMS report details
    """
    try:
        from app.services.pdf_generator import PDFGenerator
        
        # TODO: Query actual SMS report from database
        
        generator = PDFGenerator()
        pdf_bytes = generator.generate_audit_report(
            audit_id=f"SMS-REPORT-{report_id}",
            audit_name=f"SMS Safety Report {report_id}",
            regulation="ICAO Annex 19",
            territory="GLOBAL",
            findings=[],
            rca_records=[],
            sms_reports=[{
                "report_id": report_id,
                "risk_level": "CRITICAL",
                "status": "OPEN",
                "description": "Safety incident requiring immediate attention"
            }]
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=sms_{report_id}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating SMS PDF for {report_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
