import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class Amenity(Base):
    __tablename__ = "amenities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    requires_configuration = Column(Boolean, default=False)
    is_chargeable = Column(Boolean, default=False)
    default_price = Column(Numeric(12, 2))
    currency = Column(String, default='INR')
    meta = Column(JSONB, default={})
    is_deleted = Column(Boolean, default=False)

    options = relationship("AmenityOption", back_populates="amenity")
    property_amenities = relationship("PropertyAmenity", back_populates="amenity")

class AmenityOption(Base):
    __tablename__ = "amenity_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amenity_id = Column(UUID(as_uuid=True), ForeignKey("amenities.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(12, 2), default=0)
    currency = Column(String, default='INR')
    meta = Column(JSONB, default={})
    is_deleted = Column(Boolean, default=False)

    amenity = relationship("Amenity", back_populates="options")

    __table_args__ = (UniqueConstraint('amenity_id', 'code', name='uq_amenity_option_code'),)

class PropertyAmenity(Base):
    __tablename__ = "property_amenities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    amenity_id = Column(UUID(as_uuid=True), ForeignKey("amenities.id", ondelete="RESTRICT"), nullable=False)
    enabled = Column(Boolean, default=True)
    is_chargeable = Column(Boolean, default=False)
    price = Column(Numeric(12, 2))
    currency = Column(String, default='INR')
    apply_on = Column(String, default='per_stay')
    config = Column(JSONB, default={})

    property = relationship("Property", back_populates="property_amenities")
    amenity = relationship("Amenity", back_populates="property_amenities")

    __table_args__ = (UniqueConstraint('property_id', 'amenity_id', name='uq_property_amenity'),)
