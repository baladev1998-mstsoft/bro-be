import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Package(Base):
    __tablename__ = "packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True)
    description = Column(Text)
    base_price = Column(Numeric(12, 2))
    duration_days = Column(Integer)
    inclusions = Column(Text)
    exclusions = Column(Text)
    destination_id = Column(UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="SET NULL"))
    is_published = Column(Boolean, default=False)

    destination = relationship("Destination", back_populates="packages")
    items = relationship("PackageItem", back_populates="package")

class PackageItem(Base):
    __tablename__ = "package_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    item_type = Column(String, nullable=False)
    item_ref = Column(UUID(as_uuid=True))
    day = Column(Integer, default=1)
    description = Column(Text)

    package = relationship("Package", back_populates="items")

class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True)
    duration_days = Column(Integer)
    description = Column(Text)

    days = relationship("ItineraryDay", back_populates="itinerary")

class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False)
    day = Column(Integer, nullable=False)
    title = Column(String)
    details = Column(Text)

    itinerary = relationship("Itinerary", back_populates="days")
