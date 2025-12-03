from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel

# Offer Schemas
class OfferBase(BaseModel):
    title: str
    code: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    discount: Optional[Dict[str, Any]] = None
    applicable_to: Optional[Dict[str, Any]] = None
    is_active: bool = True

class OfferCreate(OfferBase):
    pass

class OfferUpdate(OfferBase):
    pass

class Offer(OfferBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
