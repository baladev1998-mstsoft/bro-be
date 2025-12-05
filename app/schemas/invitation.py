from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class InvitationCreate(BaseModel):
    email: EmailStr
    role: str
    property_id: Optional[UUID] = None
    expires_in_minutes: int = 1440 # 24 hours
    message: Optional[str] = None

class InvitationResponse(BaseModel):
    token: str
    expires_at: datetime

class InvitationAccept(BaseModel):
    token: str
    full_name: str
    password: str
