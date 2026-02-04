"""
Evidence Service - Universal Evidence Management
Handles upload, compression, encryption, and integrity verification
"""
from sqlalchemy.orm import Session
from typing import Optional, BinaryIO
from datetime import datetime
import hashlib
import os
import uuid
from PIL import Image
import io
from cryptography.fernet import Fernet
from PyPDF2 import PdfReader, PdfWriter

from app.models.evidence_vault import EvidenceVault
from app.models.system_audit_log import SystemAuditLog


class EvidenceService:
    """
    Universal Evidence Management Service
    
    Features:
    - Intelligent compression (max 2MB)
    - AES-256 encryption at rest
    - SHA-256 integrity verification
    - 5-year legal custody
    - Soft delete only
    """
    
    # Configuration
    MAX_FILE_SIZE_MB = 2
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    STORAGE_BASE_PATH = "/var/ontrackia/evidence_vault"
    ENCRYPTION_KEY = os.getenv("EVIDENCE_ENCRYPTION_KEY")  # Must be set in .env
    
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        
        # Initialize encryption
        if not self.ENCRYPTION_KEY:
            raise ValueError("EVIDENCE_ENCRYPTION_KEY not set in environment")
        self.cipher = Fernet(self.ENCRYPTION_KEY.encode())
    
    def upload_evidence(
        self,
        file: BinaryIO,
        filename: str,
        entity_type: str,
        entity_id: str,
        uploaded_by: int,
        uploaded_by_name: str,
        description: Optional[str] = None,
        tags: Optional[dict] = None
    ) -> EvidenceVault:
        """
        Upload evidence with automatic compression and encryption.
        
        Steps:
        1. Read original file
        2. Calculate original hash
        3. Compress if needed (images/PDFs)
        4. Encrypt compressed file
        5. Save to vault
        6. Create database record
        7. Log to audit trail
        """
        # Read original file
        file_content = file.read()
        original_size = len(file_content)
        
        # Calculate original hash
        original_hash = hashlib.sha256(file_content).hexdigest()
        
        # Determine file type
        file_extension = os.path.splitext(filename)[1].lower()
        evidence_type = self._determine_evidence_type(file_extension)
        
        # Compress if needed
        compressed_content, compression_ratio = self._compress_file(
            file_content, 
            file_extension
        )
        compressed_size = len(compressed_content)
        
        # Encrypt
        encrypted_content = self.cipher.encrypt(compressed_content)
        encrypted_hash = hashlib.sha256(encrypted_content).hexdigest()
        
        # Generate evidence ID
        evidence_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Save to disk
        encrypted_file_path = self._save_to_vault(
            encrypted_content,
            evidence_id,
            file_extension
        )
        
        # Create database record
        evidence = EvidenceVault(
            tenant_id=1,  # TODO: Get from context
            organization_id=self.organization_id,
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            entity_type=entity_type,
            entity_id=entity_id,
            original_filename=filename,
            file_extension=file_extension,
            mime_type=self._get_mime_type(file_extension),
            original_size_bytes=original_size,
            compressed_size_bytes=compressed_size,
            compression_ratio=compression_ratio,
            encrypted_file_path=encrypted_file_path,
            encryption_key_id="default",  # TODO: Key rotation
            file_hash_sha256=original_hash,
            encrypted_hash_sha256=encrypted_hash,
            description=description,
            tags=tags,
            uploaded_by=uploaded_by,
            uploaded_by_name=uploaded_by_name,
            retention_until=EvidenceVault.calculate_retention_date()
        )
        
        self.db.add(evidence)
        self.db.flush()
        
        # Log to audit trail
        self._log_upload(evidence, uploaded_by)
        
        self.db.commit()
        self.db.refresh(evidence)
        
        print(f"✅ Evidence uploaded: {evidence_id} | Original: {original_size/1024:.1f}KB → Compressed: {compressed_size/1024:.1f}KB ({compression_ratio})")
        
        return evidence
    
    def _compress_file(self, content: bytes, extension: str) -> tuple:
        """
        Compress file intelligently based on type.
        
        Images: Resize and optimize (JPEG quality 85)
        PDFs: Compress images within PDF
        Others: No compression
        """
        if extension in ['.jpg', '.jpeg', '.png', '.webp']:
            return self._compress_image(content)
        elif extension == '.pdf':
            return self._compress_pdf(content)
        else:
            return content, "0%"
    
    def _compress_image(self, content: bytes) -> tuple:
        """Compress image to max 2MB"""
        img = Image.open(io.BytesIO(content))
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Calculate target size
        original_size = len(content)
        
        # Resize if too large
        max_dimension = 2048
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Compress with quality adjustment
        output = io.BytesIO()
        quality = 85
        
        while quality > 20:
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            if output.tell() <= self.MAX_FILE_SIZE_BYTES:
                break
            
            quality -= 5
        
        compressed_content = output.getvalue()
        compressed_size = len(compressed_content)
        
        ratio = f"{int((1 - compressed_size/original_size) * 100)}%"
        
        return compressed_content, ratio
    
    def _compress_pdf(self, content: bytes) -> tuple:
        """Compress PDF by optimizing images"""
        # TODO: Implement PDF compression
        # For now, return original if under 2MB
        if len(content) <= self.MAX_FILE_SIZE_BYTES:
            return content, "0%"
        else:
            raise ValueError(f"PDF too large: {len(content)/1024/1024:.1f}MB (max 2MB)")
    
    def _save_to_vault(self, encrypted_content: bytes, evidence_id: str, extension: str) -> str:
        """Save encrypted file to vault"""
        # Create directory structure: /var/ontrackia/evidence_vault/{org_id}/{year}/{month}/
        year = datetime.utcnow().year
        month = datetime.utcnow().month
        
        vault_dir = os.path.join(
            self.STORAGE_BASE_PATH,
            str(self.organization_id),
            str(year),
            f"{month:02d}"
        )
        
        os.makedirs(vault_dir, exist_ok=True)
        
        # Save file
        filename = f"{evidence_id}{extension}.enc"
        file_path = os.path.join(vault_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(encrypted_content)
        
        return file_path
    
    def retrieve_evidence(self, evidence_id: str) -> tuple:
        """
        Retrieve and decrypt evidence.
        
        Returns: (decrypted_content, evidence_record)
        """
        evidence = self.db.query(EvidenceVault).filter(
            EvidenceVault.evidence_id == evidence_id,
            EvidenceVault.organization_id == self.organization_id,
            EvidenceVault.is_deleted == False
        ).first()
        
        if not evidence:
            raise ValueError(f"Evidence not found: {evidence_id}")
        
        # Read encrypted file
        with open(evidence.encrypted_file_path, 'rb') as f:
            encrypted_content = f.read()
        
        # Verify encrypted hash
        encrypted_hash = hashlib.sha256(encrypted_content).hexdigest()
        if encrypted_hash != evidence.encrypted_hash_sha256:
            raise ValueError(f"Evidence integrity compromised: {evidence_id}")
        
        # Decrypt
        decrypted_content = self.cipher.decrypt(encrypted_content)
        
        # Verify original hash
        original_hash = hashlib.sha256(decrypted_content).hexdigest()
        if original_hash != evidence.file_hash_sha256:
            raise ValueError(f"Evidence integrity compromised after decryption: {evidence_id}")
        
        return decrypted_content, evidence
    
    def soft_delete_evidence(
        self,
        evidence_id: str,
        deleted_by: int,
        reason: str
    ):
        """Soft delete evidence (never physically deleted)"""
        evidence = self.db.query(EvidenceVault).filter(
            EvidenceVault.evidence_id == evidence_id,
            EvidenceVault.organization_id == self.organization_id
        ).first()
        
        if not evidence:
            raise ValueError(f"Evidence not found: {evidence_id}")
        
        if not evidence.can_be_deleted():
            raise ValueError(
                f"Evidence cannot be deleted before retention period expires: "
                f"{evidence.retention_until.isoformat()}"
            )
        
        evidence.soft_delete(deleted_by, reason)
        
        # Log to audit trail
        self._log_deletion(evidence, deleted_by, reason)
        
        self.db.commit()
    
    def _determine_evidence_type(self, extension: str) -> str:
        """Determine evidence type from extension"""
        image_exts = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        video_exts = ['.mp4', '.mov', '.avi']
        doc_exts = ['.pdf', '.doc', '.docx', '.txt']
        
        if extension in image_exts:
            return "PHOTO"
        elif extension in video_exts:
            return "VIDEO"
        elif extension in doc_exts:
            return "DOCUMENT"
        else:
            return "OTHER"
    
    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type from extension"""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.mp4': 'video/mp4'
        }
        return mime_types.get(extension, 'application/octet-stream')
    
    def _log_upload(self, evidence: EvidenceVault, user_id: int):
        """Log evidence upload to audit trail"""
        # TODO: Integrate with SystemAuditLog
        pass
    
    def _log_deletion(self, evidence: EvidenceVault, user_id: int, reason: str):
        """Log evidence deletion to audit trail"""
        # TODO: Integrate with SystemAuditLog
        pass
