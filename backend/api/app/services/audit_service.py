"""
Audit Service - CRUD Operations for Audit Contexts, Findings, and RCA
Implements Row-Level Security and data inheritance protocol
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, and_
from typing import List, Optional, Dict
from datetime import datetime
import hashlib
import json

from app.models.audit_models import (
    AuditContext, Component, Finding, RCARecord, AuditTrailEntry
)
from app.database import set_tenant_context


class AuditService:
    """Service for managing audit operations with PostgreSQL"""
    
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        # Set RLS context
        set_tenant_context(db, organization_id)
    
    # ==========================================
    # AUDIT CONTEXT
    # ==========================================
    
    def create_audit_context(
        self,
        audit_id: str,
        territory: str,
        regulation: str,
        scope: Dict,
        created_by: int
    ) -> AuditContext:
        """Create new audit context"""
        
        # Calculate scope hash
        scope_json = json.dumps(scope, sort_keys=True)
        scope_hash = hashlib.sha256(scope_json.encode()).hexdigest()
        
        audit = AuditContext(
            organization_id=self.organization_id,
            audit_id=audit_id,
            territory=territory,
            regulation=regulation,
            scope=scope,
            scope_hash=scope_hash,
            created_by=created_by
        )
        
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        
        # Create audit trail entry
        self._create_trail_entry(
            entity_type="audit_context",
            entity_id=audit.audit_id,
            action="created",
            user_id=created_by,
            data={"scope": scope}
        )
        
        return audit
    
    def get_audit_context(self, audit_id: str) -> Optional[AuditContext]:
        """Get audit context by ID"""
        return self.db.query(AuditContext).filter(
            AuditContext.audit_id == audit_id,
            AuditContext.organization_id == self.organization_id
        ).first()
    
    def list_audit_contexts(
        self,
        territory: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[AuditContext]:
        """List audit contexts with filters"""
        query = self.db.query(AuditContext).filter(
            AuditContext.organization_id == self.organization_id
        )
        
        if territory:
            query = query.filter(AuditContext.territory == territory)
        if status:
            query = query.filter(AuditContext.status == status)
        
        return query.order_by(AuditContext.created_at.desc()).limit(limit).all()
    
    # ==========================================
    # COMPONENTS
    # ==========================================
    
    def create_component(
        self,
        audit_id: str,
        component_id: str,
        component_type: str,
        description: str,
        created_by: int,
        metadata: Optional[Dict] = None
    ) -> Component:
        """Create component linked to audit"""
        
        # Get audit context
        audit = self.get_audit_context(audit_id)
        if not audit:
            raise ValueError(f"Audit {audit_id} not found")
        
        # Inherit scope from audit
        inherited_scope = {
            "audit_id": audit.audit_id,
            "territory": audit.territory,
            "regulation": audit.regulation,
            **audit.scope
        }
        
        component = Component(
            organization_id=self.organization_id,
            component_id=component_id,
            component_type=component_type,
            description=description,
            audit_context_id=audit.id,
            inherited_audit_id=audit.audit_id,
            inherited_scope=inherited_scope,
            metadata=metadata or {},
            created_by=created_by
        )
        
        self.db.add(component)
        self.db.commit()
        self.db.refresh(component)
        
        return component
    
    # ==========================================
    # FINDINGS
    # ==========================================
    
    def create_finding(
        self,
        finding_id: str,
        component_id: str,
        level: int,
        description: str,
        regulation_reference: str,
        created_by: int,
        severity: Optional[str] = None,
        evidence: Optional[Dict] = None
    ) -> Finding:
        """Create finding linked to component"""
        
        # Get component
        component = self.db.query(Component).filter(
            Component.component_id == component_id,
            Component.organization_id == self.organization_id
        ).first()
        
        if not component:
            raise ValueError(f"Component {component_id} not found")
        
        # Inherit data from component
        inherited_finding = {
            "component_id": component.component_id,
            "component_type": component.component_type,
            "description": component.description
        }
        
        finding = Finding(
            organization_id=self.organization_id,
            finding_id=finding_id,
            level=level,
            description=description,
            regulation_reference=regulation_reference,
            severity=severity or "medium",
            component_id=component.id,
            inherited_audit_id=component.inherited_audit_id,
            inherited_scope=component.inherited_scope,
            inherited_finding=inherited_finding,
            evidence=evidence or {},
            created_by=created_by
        )
        
        self.db.add(finding)
        self.db.commit()
        self.db.refresh(finding)
        
        # Create audit trail
        self._create_trail_entry(
            entity_type="finding",
            entity_id=finding.finding_id,
            action="created",
            user_id=created_by,
            data={"level": level, "severity": severity}
        )
        
        return finding
    
    def list_findings(
        self,
        audit_id: Optional[str] = None,
        component_id: Optional[str] = None,
        level: Optional[int] = None,
        limit: int = 100
    ) -> List[Finding]:
        """List findings with filters"""
        query = self.db.query(Finding).filter(
            Finding.organization_id == self.organization_id
        )
        
        if audit_id:
            query = query.filter(Finding.inherited_audit_id == audit_id)
        if component_id:
            component = self.db.query(Component).filter(
                Component.component_id == component_id
            ).first()
            if component:
                query = query.filter(Finding.component_id == component.id)
        if level:
            query = query.filter(Finding.level == level)
        
        return query.order_by(Finding.created_at.desc()).limit(limit).all()
    
    # ==========================================
    # ROOT CAUSE ANALYSIS
    # ==========================================
    
    def create_rca(
        self,
        rca_id: str,
        finding_id: str,
        root_cause: str,
        corrective_action: str,
        created_by: int,
        preventive_action: Optional[str] = None,
        ai_assisted: bool = False,
        ai_suggestion: Optional[str] = None
    ) -> RCARecord:
        """Create RCA record linked to finding"""
        
        # Get finding
        finding = self.db.query(Finding).filter(
            Finding.finding_id == finding_id,
            Finding.organization_id == self.organization_id
        ).first()
        
        if not finding:
            raise ValueError(f"Finding {finding_id} not found")
        
        rca = RCARecord(
            organization_id=self.organization_id,
            rca_id=rca_id,
            root_cause=root_cause,
            corrective_action=corrective_action,
            preventive_action=preventive_action,
            finding_id=finding.id,
            inherited_audit_id=finding.inherited_audit_id,
            inherited_scope=finding.inherited_scope,
            inherited_finding=finding.inherited_finding,
            ai_assisted=ai_assisted,
            ai_suggestion=ai_suggestion,
            created_by=created_by
        )
        
        self.db.add(rca)
        self.db.commit()
        self.db.refresh(rca)
        
        # Create audit trail
        self._create_trail_entry(
            entity_type="rca",
            entity_id=rca.rca_id,
            action="created",
            user_id=created_by,
            data={"ai_assisted": ai_assisted}
        )
        
        return rca
    
    def list_rcas(
        self,
        audit_id: Optional[str] = None,
        finding_id: Optional[str] = None,
        limit: int = 100
    ) -> List[RCARecord]:
        """List RCA records with filters"""
        query = self.db.query(RCARecord).filter(
            RCARecord.organization_id == self.organization_id
        )
        
        if audit_id:
            query = query.filter(RCARecord.inherited_audit_id == audit_id)
        if finding_id:
            finding = self.db.query(Finding).filter(
                Finding.finding_id == finding_id
            ).first()
            if finding:
                query = query.filter(RCARecord.finding_id == finding.id)
        
        return query.order_by(RCARecord.created_at.desc()).limit(limit).all()
    
    # ==========================================
    # AUDIT TRAIL
    # ==========================================
    
    def _create_trail_entry(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        user_id: int,
        data: Dict
    ) -> AuditTrailEntry:
        """Create immutable audit trail entry"""
        
        # Get previous hash for blockchain-like chain
        last_entry = self.db.query(AuditTrailEntry).filter(
            AuditTrailEntry.organization_id == self.organization_id
        ).order_by(AuditTrailEntry.created_at.desc()).first()
        
        previous_hash = last_entry.entry_hash if last_entry else "0" * 64
        
        # Calculate entry hash
        entry_data = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "user_id": user_id,
            "data": data,
            "previous_hash": previous_hash,
            "timestamp": datetime.utcnow().isoformat()
        }
        entry_json = json.dumps(entry_data, sort_keys=True)
        entry_hash = hashlib.sha256(entry_json.encode()).hexdigest()
        
        trail = AuditTrailEntry(
            organization_id=self.organization_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            data=data,
            previous_hash=previous_hash,
            entry_hash=entry_hash
        )
        
        self.db.add(trail)
        self.db.commit()
        
        return trail
    
    def get_audit_trail(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditTrailEntry]:
        """Get audit trail entries"""
        query = self.db.query(AuditTrailEntry).filter(
            AuditTrailEntry.organization_id == self.organization_id
        )
        
        if entity_type:
            query = query.filter(AuditTrailEntry.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditTrailEntry.entity_id == entity_id)
        
        return query.order_by(AuditTrailEntry.created_at.desc()).limit(limit).all()
