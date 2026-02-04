"""
Evidence Vault Model - Legal Custody System
AES-256 encryption + SHA-256 integrity + 5-year retention
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, BigInteger, Index
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import hashlib
import os
from cryptography.fernet import Fernet

from app.database import Base


class EvidenceVault(Base):
    """
    Evidence Vault - Encrypted storage with legal custody
    
    Features:
    - AES-256 encryption at rest
    - SHA-256 integrity verification
    - 5-year retention policy (EASA/CASA)
    - Soft delete (never physically deleted)
    - RLS tenant isolation
    """
    __tablename__ = "evidence_vault"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant Isolation (RLS)
    tenant_id = Column(Integer, nullable=False, index=True)
    organization_id = Column(Integer, nullable=False, index=True)
    
    # Evidence Metadata
    evidence_id = Column(String(100), unique=True, nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False, index=True)  # PHOTO, PDF, DOCUMENT, VIDEO
    
    # Linked Entity (Universal)
    entity_type = Column(String(100), nullable=False, index=True)  # CHECKLIST, FINDING, CAPA, SMS, AUDIT
    entity_id = Column(String(255), nullable=False, index=True)
    
    # File Information
    original_filename = Column(String(255), nullable=False)
    file_extension = Column(String(10), nullable=False)
    mime_type = Column(String(100))
    original_size_bytes = Column(BigInteger)  # Tamaño original
    compressed_size_bytes = Column(BigInteger)  # Tamaño después de compresión
    compression_ratio = Column(String(20))  # Ej: "75%" (reducción)
    
    # Storage
    encrypted_file_path = Column(Text, nullable=False)  # Ruta al archivo encriptado
    encryption_key_id = Column(String(100))  # ID de la clave de encriptación
    
    # Integrity
    file_hash_sha256 = Column(String(64), nullable=False, unique=True)  # Hash del archivo original
    encrypted_hash_sha256 = Column(String(64), nullable=False)  # Hash del archivo encriptado
    
    # Metadata
    description = Column(Text)
    tags = Column(JSON)  # Tags para búsqueda
    
    # Authorship (Critical for legal evidence)
    uploaded_by = Column(Integer, nullable=False, index=True)
    uploaded_by_name = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Legal Custody
    retention_until = Column(DateTime(timezone=True), nullable=False, index=True)  # 5 años desde upload
    is_deleted = Column(Boolean, default=False, index=True)  # Soft delete
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(Integer)
    deletion_reason = Column(Text)
    
    # Audit Trail Reference
    audit_log_id = Column(Integer)  # Link to system_audit_logs
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_evidence_tenant_entity', 'tenant_id', 'entity_type', 'entity_id'),
        Index('idx_evidence_uploaded', 'uploaded_by', 'uploaded_at'),
        Index('idx_evidence_retention', 'retention_until', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Evidence {self.evidence_id}: {self.original_filename}>"
    
    @staticmethod
    def calculate_retention_date() -> datetime:
        """Calculate retention date (5 years from now)"""
        return datetime.utcnow() + timedelta(days=5*365)
    
    def verify_integrity(self, file_path: str) -> bool:
        """Verify file integrity by recalculating SHA-256"""
        with open(file_path, 'rb') as f:
            file_content = f.read()
            calculated_hash = hashlib.sha256(file_content).hexdigest()
        return calculated_hash == self.file_hash_sha256
    
    def can_be_deleted(self) -> bool:
        """Check if evidence can be deleted (retention period expired)"""
        return datetime.utcnow() > self.retention_until
    
    def soft_delete(self, deleted_by: int, reason: str):
        """Soft delete - mark as deleted but keep file"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by
        self.deletion_reason = reason


class KnowledgeDocument(Base):
    """
    Knowledge Document - MOE, Quality Manuals, Procedures
    
    Stored in RAG for AI-assisted auditing.
    Prioritized over general regulations.
    """
    __tablename__ = "knowledge_documents"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant Isolation (RLS)
    tenant_id = Column(Integer, nullable=False, index=True)
    organization_id = Column(Integer, nullable=False, index=True)
    
    # Document Metadata
    document_id = Column(String(100), unique=True, nullable=False, index=True)
    document_type = Column(String(50), nullable=False, index=True)  # MOE, QUALITY_MANUAL, PROCEDURE, SOP
    
    # Content
    title = Column(String(500), nullable=False)
    description = Column(Text)
    original_filename = Column(String(255), nullable=False)
    
    # Storage
    encrypted_file_path = Column(Text, nullable=False)
    file_hash_sha256 = Column(String(64), nullable=False)
    
    # RAG Integration
    is_indexed = Column(Boolean, default=False, index=True)
    indexed_at = Column(DateTime(timezone=True))
    chunk_count = Column(Integer)  # Número de chunks en ChromaDB
    vector_collection_id = Column(String(100))  # ID en ChromaDB
    
    # Priority (for RAG retrieval)
    priority = Column(Integer, default=100)  # Higher = more priority (MOE = 100, general regs = 50)
    
    # Versioning
    version = Column(String(20), default="1.0")
    supersedes_document_id = Column(String(100))  # ID del documento que reemplaza
    is_active = Column(Boolean, default=True, index=True)
    
    # Authorship
    uploaded_by = Column(Integer, nullable=False)
    uploaded_by_name = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Legal Custody
    retention_until = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_knowledge_tenant_type', 'tenant_id', 'document_type', 'is_active'),
        Index('idx_knowledge_indexed', 'is_indexed', 'priority'),
    )
    
    def __repr__(self):
        return f"<KnowledgeDoc {self.document_id}: {self.title}>"
