"""
Master Audit Log Model - Aviation-Grade Traceability
Immutable black box for FAA/EASA/CASA compliance
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index
from sqlalchemy.sql import func
from datetime import datetime
import hashlib
import json

from app.database import Base


class SystemAuditLog(Base):
    """
    Master Audit Log - Immutable Black Box
    
    Records every action in the system with forensic integrity.
    Compliant with FAA/EASA/CASA traceability requirements.
    """
    __tablename__ = "system_audit_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant Isolation (RLS)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # User Information
    user_id = Column(Integer, nullable=False, index=True)
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255))
    
    # Action Details
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)  # CREATE, UPDATE, DELETE, CLOSE, VALIDATE
    action_description = Column(Text, nullable=False)
    
    # Entity Information
    entity_type = Column(String(100), nullable=False, index=True)  # AUDIT, FINDING, RCA, SMS, CAPA
    entity_id = Column(String(255), nullable=False, index=True)
    
    # Change Tracking
    previous_state = Column(JSON)  # Estado anterior (JSON)
    new_state = Column(JSON)  # Estado nuevo (JSON)
    changes_summary = Column(Text)  # Resumen legible de cambios
    
    # Forensic Information
    ip_address = Column(String(45))  # IPv4 o IPv6
    user_agent = Column(Text)
    device_info = Column(JSON)
    
    # Request Context
    request_id = Column(String(100))  # UUID de la request
    endpoint = Column(String(255))  # API endpoint llamado
    http_method = Column(String(10))  # GET, POST, PUT, DELETE
    
    # Integrity Hash (SHA-256)
    entry_hash = Column(String(64), nullable=False, unique=True)  # Hash de esta entrada
    previous_hash = Column(String(64))  # Hash de la entrada anterior (blockchain-like)
    
    # Metadata
    severity = Column(String(20), default="INFO")  # INFO, WARNING, CRITICAL
    tags = Column(JSON)  # Tags adicionales para búsqueda
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_tenant_timestamp', 'tenant_id', 'timestamp'),
        Index('idx_audit_user_action', 'user_id', 'action_type'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_timestamp_desc', 'timestamp', postgresql_ops={'timestamp': 'DESC'}),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action_type} on {self.entity_type}/{self.entity_id}>"
    
    @staticmethod
    def calculate_hash(
        timestamp: datetime,
        user_id: int,
        action_type: str,
        entity_type: str,
        entity_id: str,
        new_state: dict,
        previous_hash: str = None
    ) -> str:
        """Calculate SHA-256 hash for entry integrity"""
        content = {
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "action_type": action_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "new_state": new_state,
            "previous_hash": previous_hash or "0" * 64
        }
        content_json = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_json.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify entry integrity by recalculating hash"""
        calculated_hash = self.calculate_hash(
            timestamp=self.timestamp,
            user_id=self.user_id,
            action_type=self.action_type,
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            new_state=self.new_state or {},
            previous_hash=self.previous_hash
        )
        return calculated_hash == self.entry_hash
