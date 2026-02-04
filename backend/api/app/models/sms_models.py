"""
SMS (Safety Management System) Database Models
ICAO Annex 19 compliant with forensic integrity
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database import Base


class SMSReport(Base):
    """
    SMS Safety Report with ICAO 5x5 Risk Matrix
    Includes SHA-256 for forensic integrity
    """
    __tablename__ = "sms_reports"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(String(50), unique=True, nullable=False, index=True)  # SMS-XXXXX
    
    # Source & Description
    source = Column(String(50), nullable=False)  # AUDIT_AUTO, VOLUNTARY_ANONYMOUS, SUPERVISOR_MANUAL
    description = Column(Text, nullable=False)
    
    # Territory & Evidence
    territory = Column(String(50), nullable=True, index=True)
    evidence_id = Column(String(100), nullable=True)
    
    # Risk Assessment (ICAO 5x5 Matrix)
    compliance_score = Column(Integer, nullable=True)
    risk_level = Column(String(20), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    risk_score = Column(Integer, nullable=False)  # severity * probability
    severity = Column(Integer, nullable=False)  # 1-5
    severity_label = Column(String(50), nullable=False)
    probability = Column(Integer, nullable=False)  # 1-5
    probability_label = Column(String(50), nullable=False)
    
    # Actions & Status
    suggested_action = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="OPEN", index=True)  # OPEN, REVIEWING, CLOSED
    
    # Forensic Integrity
    sha256_hash = Column(String(64), nullable=False, index=True)
    
    # Review tracking
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Metadata
    photo_hash = Column(String(64), nullable=True)
    has_attachment = Column(Boolean, default=False)
    meta = Column(JSONB, nullable=True)
    
    # Inheritance from Audit (if escalated)
    inherited_audit_id = Column(String(50), nullable=True)
    inherited_scope = Column(JSONB, nullable=True)
    inherited_finding = Column(JSONB, nullable=True)
    inherited_component = Column(JSONB, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_sms_reports_status_risk', 'status', 'risk_level'),
        Index('idx_sms_reports_territory_timestamp', 'territory', 'timestamp'),
    )


class RiskMatrix(Base):
    """
    ICAO 5x5 Risk Matrix Reference Table
    Stores severity and probability definitions
    """
    __tablename__ = "risk_matrix"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    matrix_type = Column(String(20), nullable=False, default="ICAO_5x5")
    
    # Severity or Probability
    dimension = Column(String(20), nullable=False)  # SEVERITY or PROBABILITY
    value = Column(Integer, nullable=False)  # 1-5
    label = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_risk_matrix_dimension_value', 'dimension', 'value'),
    )
