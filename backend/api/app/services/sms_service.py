"""
SMS Service - CRUD Operations for Safety Management System Reports
Implements ICAO 5x5 Risk Matrix and forensic integrity
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict
from datetime import datetime
import hashlib
import json

from app.models.sms_models import SMSReport, RiskMatrix
from app.database import set_tenant_context


class SMSService:
    """Service for managing SMS operations with PostgreSQL"""
    
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        # Set RLS context
        set_tenant_context(db, organization_id)
    
    # ==========================================
    # SMS REPORTS
    # ==========================================
    
    def create_sms_report(
        self,
        report_id: str,
        territory: str,
        event_description: str,
        severity: int,
        probability: int,
        created_by: int,
        inherited_audit_id: Optional[str] = None,
        inherited_scope: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> SMSReport:
        """Create SMS safety report with ICAO 5x5 matrix"""
        
        # Calculate risk level
        risk_score = severity * probability
        if risk_score >= 20:
            risk_level = "CRITICAL"
        elif risk_score >= 12:
            risk_level = "HIGH"
        elif risk_score >= 6:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Calculate report hash
        report_data = {
            "report_id": report_id,
            "territory": territory,
            "event_description": event_description,
            "severity": severity,
            "probability": probability,
            "timestamp": datetime.utcnow().isoformat()
        }
        report_json = json.dumps(report_data, sort_keys=True)
        report_hash = hashlib.sha256(report_json.encode()).hexdigest()
        
        report = SMSReport(
            organization_id=self.organization_id,
            report_id=report_id,
            territory=territory,
            event_description=event_description,
            severity=severity,
            probability=probability,
            risk_score=risk_score,
            risk_level=risk_level,
            inherited_audit_id=inherited_audit_id,
            inherited_scope=inherited_scope or {},
            metadata=metadata or {},
            report_hash=report_hash,
            created_by=created_by
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_sms_report(self, report_id: str) -> Optional[SMSReport]:
        """Get SMS report by ID"""
        return self.db.query(SMSReport).filter(
            SMSReport.report_id == report_id,
            SMSReport.organization_id == self.organization_id
        ).first()
    
    def list_sms_reports(
        self,
        territory: Optional[str] = None,
        risk_level: Optional[str] = None,
        audit_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SMSReport]:
        """List SMS reports with filters"""
        query = self.db.query(SMSReport).filter(
            SMSReport.organization_id == self.organization_id
        )
        
        if territory:
            query = query.filter(SMSReport.territory == territory)
        if risk_level:
            query = query.filter(SMSReport.risk_level == risk_level)
        if audit_id:
            query = query.filter(SMSReport.inherited_audit_id == audit_id)
        
        return query.order_by(SMSReport.created_at.desc()).limit(limit).all()
    
    def update_sms_report(
        self,
        report_id: str,
        updates: Dict,
        updated_by: int
    ) -> Optional[SMSReport]:
        """Update SMS report (recalculates hash)"""
        report = self.get_sms_report(report_id)
        if not report:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(report, key) and key not in ['id', 'report_id', 'organization_id', 'created_at']:
                setattr(report, key, value)
        
        # Recalculate risk if severity/probability changed
        if 'severity' in updates or 'probability' in updates:
            report.risk_score = report.severity * report.probability
            if report.risk_score >= 20:
                report.risk_level = "CRITICAL"
            elif report.risk_score >= 12:
                report.risk_level = "HIGH"
            elif report.risk_score >= 6:
                report.risk_level = "MEDIUM"
            else:
                report.risk_level = "LOW"
        
        # Recalculate hash
        report_data = {
            "report_id": report.report_id,
            "territory": report.territory,
            "event_description": report.event_description,
            "severity": report.severity,
            "probability": report.probability,
            "timestamp": datetime.utcnow().isoformat()
        }
        report_json = json.dumps(report_data, sort_keys=True)
        report.report_hash = hashlib.sha256(report_json.encode()).hexdigest()
        
        report.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    # ==========================================
    # RISK MATRIX
    # ==========================================
    
    def get_risk_matrix(self, matrix_type: str = "ICAO_5x5") -> Dict:
        """Get ICAO 5x5 risk matrix"""
        severity_levels = self.db.query(RiskMatrix).filter(
            RiskMatrix.matrix_type == matrix_type,
            RiskMatrix.dimension == "SEVERITY"
        ).order_by(RiskMatrix.value).all()
        
        probability_levels = self.db.query(RiskMatrix).filter(
            RiskMatrix.matrix_type == matrix_type,
            RiskMatrix.dimension == "PROBABILITY"
        ).order_by(RiskMatrix.value).all()
        
        return {
            "matrix_type": matrix_type,
            "severity": [
                {
                    "value": s.value,
                    "label": s.label,
                    "description": s.description
                }
                for s in severity_levels
            ],
            "probability": [
                {
                    "value": p.value,
                    "label": p.label,
                    "description": p.description
                }
                for p in probability_levels
            ]
        }
    
    def calculate_risk(self, severity: int, probability: int) -> Dict:
        """Calculate risk level from severity and probability"""
        risk_score = severity * probability
        
        if risk_score >= 20:
            risk_level = "CRITICAL"
            color = "red"
        elif risk_score >= 12:
            risk_level = "HIGH"
            color = "orange"
        elif risk_score >= 6:
            risk_level = "MEDIUM"
            color = "yellow"
        else:
            risk_level = "LOW"
            color = "green"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "color": color,
            "severity": severity,
            "probability": probability
        }
    
    # ==========================================
    # STATISTICS
    # ==========================================
    
    def get_sms_stats(self, territory: Optional[str] = None) -> Dict:
        """Get SMS statistics"""
        query = self.db.query(SMSReport).filter(
            SMSReport.organization_id == self.organization_id
        )
        
        if territory:
            query = query.filter(SMSReport.territory == territory)
        
        reports = query.all()
        
        stats = {
            "total_reports": len(reports),
            "by_risk_level": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0
            },
            "by_territory": {},
            "avg_risk_score": 0
        }
        
        total_score = 0
        for report in reports:
            stats["by_risk_level"][report.risk_level] += 1
            stats["by_territory"][report.territory] = stats["by_territory"].get(report.territory, 0) + 1
            total_score += report.risk_score
        
        if reports:
            stats["avg_risk_score"] = round(total_score / len(reports), 2)
        
        return stats
