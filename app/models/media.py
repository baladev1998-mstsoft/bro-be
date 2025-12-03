import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, BigInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String, nullable=False, default='s3')
    s3_bucket = Column(String)
    s3_key = Column(String, index=True)
    s3_etag = Column(String)
    s3_version_id = Column(String)
    url = Column(String)
    cdn_url = Column(String)
    file_name = Column(String)
    content_type = Column(String)
    size_bytes = Column(BigInteger)
    width = Column(Integer)
    height = Column(Integer)
    storage_class = Column(String)
    acl = Column(String)
    meta = Column(JSONB, default={})
    checksum = Column(String)
    uploaded_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)

    entity_media = relationship("EntityMedia", back_populates="media")

class EntityMedia(Base):
    __tablename__ = "entity_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String, nullable=False) # 'property','room_type','package','itinerary'
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(String, default='gallery') # 'hero','thumbnail','gallery','policy_doc'
    alt_text = Column(String)
    caption = Column(String)
    position = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)

    media = relationship("Media", back_populates="entity_media")

    __table_args__ = (UniqueConstraint('media_id', 'entity_type', 'entity_id', name='uq_entity_media'),)
