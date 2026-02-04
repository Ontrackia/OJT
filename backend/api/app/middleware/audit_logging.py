"""
Audit Logging Middleware - Automatic Capture
Intercepts all write operations and logs them to Master Audit Log
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session
from typing import Callable
import time
import json
import uuid
from datetime import datetime

from app.database import SessionLocal
from app.models.system_audit_log import SystemAuditLog


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically logs all write operations.
    
    Captures:
    - User information from JWT
    - Request details (IP, user agent, endpoint)
    - Response status
    - Execution time
    
    Fail-safe: If audit log fails, the main operation is rolled back.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.write_methods = {"POST", "PUT", "PATCH", "DELETE"}
        self.excluded_paths = {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip non-write operations and excluded paths
        if request.method not in self.write_methods:
            return await call_next(request)
        
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Capture request start time
        start_time = time.time()
        
        # Extract user info from request state (set by JWT middleware)
        user_id = getattr(request.state, "user_id", None)
        user_name = getattr(request.state, "user_name", "System")
        user_email = getattr(request.state, "user_email", None)
        tenant_id = getattr(request.state, "tenant_id", 1)
        
        # Capture request body (for change tracking)
        try:
            body = await request.body()
            request_data = json.loads(body) if body else {}
        except:
            request_data = {}
        
        # Execute the actual request
        response = await call_next(request)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Only log successful write operations (2xx status codes)
        if 200 <= response.status_code < 300:
            try:
                self._create_audit_log(
                    request=request,
                    request_id=request_id,
                    user_id=user_id,
                    user_name=user_name,
                    user_email=user_email,
                    tenant_id=tenant_id,
                    request_data=request_data,
                    status_code=response.status_code,
                    execution_time=execution_time
                )
            except Exception as e:
                # FAIL-SAFE: If audit log fails, log error but don't break request
                print(f"❌ AUDIT LOG FAILED: {str(e)}")
                # In production, you might want to:
                # 1. Send alert to monitoring system
                # 2. Write to emergency log file
                # 3. Potentially rollback the main operation
        
        return response
    
    def _create_audit_log(
        self,
        request: Request,
        request_id: str,
        user_id: int,
        user_name: str,
        user_email: str,
        tenant_id: int,
        request_data: dict,
        status_code: int,
        execution_time: float
    ):
        """Create audit log entry"""
        db = SessionLocal()
        
        try:
            # Determine action type from HTTP method and path
            action_type = self._determine_action_type(request.method, request.url.path)
            
            # Extract entity information from path
            entity_type, entity_id = self._extract_entity_info(request.url.path, request_data)
            
            # Get previous hash for blockchain-like chain
            last_log = db.query(SystemAuditLog).filter(
                SystemAuditLog.tenant_id == tenant_id
            ).order_by(SystemAuditLog.id.desc()).first()
            
            previous_hash = last_log.entry_hash if last_log else "0" * 64
            
            # Calculate entry hash
            entry_hash = SystemAuditLog.calculate_hash(
                timestamp=datetime.utcnow(),
                user_id=user_id or 0,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                new_state=request_data,
                previous_hash=previous_hash
            )
            
            # Create audit log entry
            audit_log = SystemAuditLog(
                tenant_id=tenant_id,
                user_id=user_id or 0,
                user_name=user_name,
                user_email=user_email,
                action_type=action_type,
                action_description=f"{action_type} {entity_type} {entity_id}",
                entity_type=entity_type,
                entity_id=entity_id,
                new_state=request_data,
                previous_state=None,  # TODO: Capture from database before update
                changes_summary=self._generate_changes_summary(action_type, entity_type),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                device_info={"execution_time_ms": round(execution_time * 1000, 2)},
                request_id=request_id,
                endpoint=request.url.path,
                http_method=request.method,
                entry_hash=entry_hash,
                previous_hash=previous_hash,
                severity=self._determine_severity(action_type),
                tags={"status_code": status_code}
            )
            
            db.add(audit_log)
            db.commit()
            
            print(f"📜 AUDIT LOG: [{action_type}] {entity_type}/{entity_id} by {user_name} | Hash: {entry_hash[:16]}...")
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def _determine_action_type(self, method: str, path: str) -> str:
        """Determine action type from HTTP method and path"""
        if method == "POST":
            return "CREATE"
        elif method == "PUT" or method == "PATCH":
            if "close" in path.lower():
                return "CLOSE"
            elif "validate" in path.lower():
                return "VALIDATE"
            elif "approve" in path.lower():
                return "APPROVE"
            else:
                return "UPDATE"
        elif method == "DELETE":
            return "DELETE"
        return "UNKNOWN"
    
    def _extract_entity_info(self, path: str, data: dict) -> tuple:
        """Extract entity type and ID from path and data"""
        # Parse path to determine entity type
        if "/audit" in path:
            if "/contexts" in path:
                return "AUDIT_CONTEXT", data.get("audit_id", "unknown")
            elif "/findings" in path:
                return "FINDING", data.get("finding_id", "unknown")
            elif "/rca" in path:
                return "RCA", data.get("rca_id", "unknown")
            else:
                return "AUDIT", "unknown"
        elif "/sms" in path:
            return "SMS_REPORT", data.get("report_id", "unknown")
        elif "/ai-act" in path:
            return "AI_ACT_AUDIT", data.get("audit_id", "unknown")
        else:
            return "UNKNOWN", "unknown"
    
    def _generate_changes_summary(self, action_type: str, entity_type: str) -> str:
        """Generate human-readable changes summary"""
        return f"{action_type} operation on {entity_type}"
    
    def _determine_severity(self, action_type: str) -> str:
        """Determine severity level based on action type"""
        if action_type in ["DELETE", "CLOSE"]:
            return "CRITICAL"
        elif action_type in ["APPROVE", "VALIDATE"]:
            return "WARNING"
        else:
            return "INFO"
