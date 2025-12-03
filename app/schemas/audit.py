from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# Audit Log Schemas
class AuditLogBase(BaseModel):
    user_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Activity Log Schemas
class ActivityLogBase(BaseModel):
    user_id: Optional[UUID] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    event: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLog(ActivityLogBase):
    id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
