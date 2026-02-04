"""
OJT (On-the-Job Training) Models
Models for training tracking and validation
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, Date
from app.models.database_models import Base
from datetime import datetime, date
import uuid

class OJTPerson(Base):
    __tablename__ = "ojt_persons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)  # Linked to users
    
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True) # Contact email
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    supervisor_id = Column(Integer, nullable=True)  # user_id of supervisor
    
    status = Column(String(20), default='active')  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<OJTPerson {self.full_name}>"

class OJTTask(Base):
    __tablename__ = "ojt_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(Integer, nullable=False, index=True)
    
    task_code = Column(String(50), nullable=False)
    task_title = Column(String(255), nullable=False)
    task_description = Column(Text, nullable=True)
    task_category = Column(String(100), nullable=True)  # Mechanical, Avionics, etc.
    normative_reference = Column(Text, nullable=True)
    
    requires_evidence = Column(Boolean, default=True)
    ai_generated_description = Column(Boolean, default=False)
    
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<OJTTask {self.task_code} - {self.task_title}>"

class OJTPersonTask(Base):
    __tablename__ = "ojt_person_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(Integer, nullable=False, index=True)
    person_id = Column(String, ForeignKey('ojt_persons.id'), nullable=False)
    task_id = Column(String, ForeignKey('ojt_tasks.id'), nullable=False)
    
    assigned_date = Column(Date, nullable=False, default=date.today)
    target_completion_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)
    
    status = Column(String(20), default='assigned')  # assigned, in_progress, completed, validated
    supervisor_validated = Column(Boolean, default=False)
    validated_by = Column(Integer, nullable=True)  # supervisor user_id
    
    # External validator info / Snapshot
    validator_name = Column(String(255), nullable=True)
    validator_email = Column(String(255), nullable=True)
    
    validated_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<OJTPersonTask {self.status}>"

class OJTEvidence(Base):
    __tablename__ = "ojt_evidences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(Integer, nullable=False, index=True)
    person_task_id = Column(String, ForeignKey('ojt_person_tasks.id'), nullable=False)
    
    evidence_type = Column(String(50), nullable=True)  # photo, document, video
    file_path = Column(Text, nullable=False)
    file_hash_sha256 = Column(String(64), nullable=False)
    
    # Geolocalización Forense (V2.0 - Trazabilidad Ultimate)
    latitude = Column(String(20), nullable=False)  # Formato: "XX.XXXXXX"
    longitude = Column(String(20), nullable=False)  # Formato: "XX.XXXXXX"
    gps_accuracy = Column(String(10), nullable=True)  # Precisión en metros
    gps_timestamp = Column(DateTime, nullable=False)  # Timestamp de captura GPS
    
    uploaded_by = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<OJTEvidence {self.evidence_type} @ ({self.latitude}, {self.longitude})>"
