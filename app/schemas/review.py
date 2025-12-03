from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# Review Schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None
    is_published: bool = True

class ReviewCreate(ReviewBase):
    user_id: Optional[UUID] = None
    property_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None

class ReviewUpdate(ReviewBase):
    pass

class Review(ReviewBase):
    id: UUID
    user_id: Optional[UUID] = None
    property_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
