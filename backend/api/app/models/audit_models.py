"""
Audit Context and Finding Database Models
Implements data inheritance flow: Scope → Component → Finding → RCA
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class AuditContext(Base):
    """
    Audit Context with heredable scope data
    Root of the inheritance chain
    """
    __tablename__ = "audit_contexts"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    audit_id = Column(String(50), unique=True, nullable=False, index=True)  # AUD-XXXXX
    
    # Scope (heredable to all children)
    audit_name = Column(String(200), nullable=False)
    regulation = Column(String(50), nullable=False)  # EASA, FAA, ICAO, etc.
    territory = Column(String(50), nullable=True, index=True)
    aircraft_type = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Forensic
    sha256_hash = Column(String(64), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    components = relationship("Component", back_populates="audit_context", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="audit_context", cascade="all, delete-orphan")
    rca_records = relationship("RCARecord", back_populates="audit_context", cascade="all, delete-orphan")


class Component(Base):
    """
    Aircraft Component with heredable metadata
    """
    __tablename__ = "components"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    audit_context_id = Column(BigInteger, ForeignKey("audit_contexts.id", ondelete="CASCADE"), nullable=False)
    
    serial_number = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=True)
    part_number = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Metadata
    meta = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    audit_context = relationship("AuditContext", back_populates="components")
    
    __table_args__ = (
        Index('idx_components_audit_serial', 'audit_context_id', 'serial_number'),
    )


class Finding(Base):
    """
    Audit Finding with inherited scope from AuditContext
    """
    __tablename__ = "findings"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    finding_id = Column(String(50), unique=True, nullable=False, index=True)  # F-XXXXX
    audit_context_id = Column(BigInteger, ForeignKey("audit_contexts.id", ondelete="CASCADE"), nullable=False)
    
    # Finding data
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    level = Column(Integer, nullable=False, index=True)  # 1=Critical, 2=Major, 3=Observation
    status = Column(String(20), nullable=False, default="OPEN", index=True)
    deadline = Column(DateTime, nullable=True)
    category = Column(String(50), nullable=True)  # OJT, MOE, SMS, AUDIT
    
    # Inheritance
    inherited_scope = Column(JSONB, nullable=False)  # From AuditContext
    inherited_component = Column(JSONB, nullable=True)  # From Component if applicable
    component_serial = Column(String(100), nullable=True)
    
    # Forensic
    sha256_hash = Column(String(64), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_context = relationship("AuditContext", back_populates="findings")
    rca_records = relationship("RCARecord", back_populates="finding", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_findings_audit_level', 'audit_context_id', 'level'),
        Index('idx_findings_status_deadline', 'status', 'deadline'),
    )


class RCARecord(Base):
    """
    Root Cause Analysis with inherited data from Finding
    """
    __tablename__ = "rca_records"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    rca_id = Column(String(50), unique=True, nullable=False, index=True)  # RCA-XXXXX
    audit_context_id = Column(BigInteger, ForeignKey("audit_contexts.id", ondelete="CASCADE"), nullable=False)
    finding_id = Column(BigInteger, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False)
    
    # RCA data
    root_cause = Column(Text, nullable=False)
    corrective_action = Column(Text, nullable=False)
    responsible = Column(String(100), nullable=True)
    target_date = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED
    
    # Inheritance
    inherited_scope = Column(JSONB, nullable=False)  # From AuditContext
    inherited_finding = Column(JSONB, nullable=False)  # From Finding
    
    # Forensic
    sha256_hash = Column(String(64), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_context = relationship("AuditContext", back_populates="rca_records")
    finding = relationship("Finding", back_populates="rca_records")


class AuditTrailEntry(Base):
    """
    Immutable audit trail for all actions
    Blockchain-like integrity with previous_hash
    """
    __tablename__ = "audit_trail"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Action details
    user_id = Column(String(100), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, ESCALATE
    entity_type = Column(String(50), nullable=False)  # AUDIT, FINDING, RCA, SMS
    entity_id = Column(String(50), nullable=False, index=True)
    
    # Change tracking
    details = Column(JSONB, nullable=True)
    previous_state = Column(JSONB, nullable=True)
    new_state = Column(JSONB, nullable=True)
    
    # Blockchain-like integrity
    sha256_hash = Column(String(64), nullable=False, unique=True, index=True)
    previous_hash = Column(String(64), nullable=True)  # Links to previous entry
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_audit_trail_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_trail_user_timestamp', 'user_id', 'timestamp'),
    )
