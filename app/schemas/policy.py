from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel

# Policy Schemas
class PolicyBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(PolicyBase):
    pass

class Policy(PolicyBase):
    id: UUID
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Property Policy Schemas
class PropertyPolicyBase(BaseModel):
    content: Optional[str] = None
    short_text: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

class PropertyPolicyCreate(PropertyPolicyBase):
    property_id: UUID
    policy_id: UUID

class PropertyPolicyUpdate(PropertyPolicyBase):
    pass

class PropertyPolicy(PropertyPolicyBase):
    id: UUID
    property_id: UUID
    policy_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    policy: Optional[Policy] = None

    class Config:
        from_attributes = True
