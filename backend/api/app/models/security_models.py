"""
Security Events Database Model
Adapted from OnTrackIA V4 Security Audit Service
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database import Base


class SecurityEvent(Base):
    """
    Security event logging for authentication, authorization, and sensitive actions
    """
    __tablename__ = "security_events"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Event details
    event_type = Column(String(60), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    actor_role = Column(String(30), nullable=True)
    organization_id = Column(BigInteger, nullable=True, index=True)  # For future multi-tenant
    
    # Target (for admin actions)
    target_user_id = Column(BigInteger, nullable=True)
    target_resource_type = Column(String(60), nullable=True)
    target_resource_id = Column(String(100), nullable=True)
    
    # Request context
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(String(500), nullable=True)
    
    # Result
    success = Column(String(10), nullable=True)  # SUCCESS or FAILURE
    failure_reason = Column(String(100), nullable=True)
    
    # Additional metadata (sanitized - no PII)
    meta = Column(JSONB, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_security_events_org_created', 'organization_id', 'created_at'),
        Index('idx_security_events_user_type', 'user_id', 'event_type'),
        Index('idx_security_events_ip_created', 'ip_address', 'created_at'),
    )
