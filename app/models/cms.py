import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, UniqueConstraint, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, backref
from app.models.base import Base

class CMSPage(Base):
    __tablename__ = "cms_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False, index=True)
    is_published = Column(Boolean, default=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("cms_pages.id", ondelete="SET NULL"), nullable=True)
    
    parent = relationship("CMSPage", remote_side=[id], backref="children")
    translations = relationship("CMSPageTranslation", back_populates="page", cascade="all, delete-orphan")
    sections = relationship("CMSSection", back_populates="page", cascade="all, delete-orphan")

class CMSPageTranslation(Base):
    __tablename__ = "cms_page_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey("cms_pages.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String, nullable=False) # e.g., 'en', 'ta'
    title = Column(String, nullable=False)
    seo_metadata = Column(JSONB, default={}) # title, description, keywords
    
    page = relationship("CMSPage", back_populates="translations")

    __table_args__ = (UniqueConstraint('page_id', 'language_code', name='uq_cms_page_translation'),)

class CMSSection(Base):
    __tablename__ = "cms_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey("cms_pages.id", ondelete="CASCADE"), nullable=False)
    section_key = Column(String, nullable=False) # e.g., 'hero', 'features'
    type = Column(String, nullable=False) # e.g., 'hero', 'text', 'gallery'
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    page = relationship("CMSPage", back_populates="sections")
    contents = relationship("CMSSectionContent", back_populates="section", cascade="all, delete-orphan")

class CMSPageVersion(Base):
    __tablename__ = "cms_page_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey("cms_pages.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    data = Column(JSONB, nullable=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    page = relationship("CMSPage", backref=backref("versions", cascade="all, delete-orphan"))

class CMSSectionContent(Base):
    __tablename__ = "cms_section_contents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("cms_sections.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String, nullable=False)
    content = Column(JSONB, default={})
    
    section = relationship("CMSSection", back_populates="contents")

    __table_args__ = (UniqueConstraint('section_id', 'language_code', name='uq_cms_section_content'),)
