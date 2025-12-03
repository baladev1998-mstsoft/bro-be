from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# Media Schemas
class MediaBase(BaseModel):
    provider: str = "s3"
    s3_bucket: Optional[str] = None
    s3_key: Optional[str] = None
    url: Optional[str] = None
    cdn_url: Optional[str] = None
    file_name: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None

class MediaCreate(MediaBase):
    uploaded_by: Optional[UUID] = None

class MediaUpdate(MediaBase):
    pass

class Media(MediaBase):
    id: UUID
    uploaded_by: Optional[UUID] = None
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Entity Media Schemas
class EntityMediaBase(BaseModel):
    entity_type: str
    entity_id: UUID
    role: Optional[str] = "gallery"
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    position: int = 0
    is_primary: bool = False

class EntityMediaCreate(EntityMediaBase):
    media_id: UUID

class EntityMediaUpdate(EntityMediaBase):
    pass

class EntityMedia(EntityMediaBase):
    id: UUID
    media_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    media: Optional[Media] = None

    class Config:
        from_attributes = True
