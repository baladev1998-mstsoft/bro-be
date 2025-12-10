import uuid
import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Integer, Date, UniqueConstraint, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class SEOMetadata(Base):
    __tablename__ = "seo_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String)
    entity_id = Column(UUID(as_uuid=True))
    meta_title = Column(String)
    meta_description = Column(String)
    meta_keywords = Column(String)
    canonical_url = Column(String)
    robots = Column(String)

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True, index=True)
    country = Column(String)
    region = Column(String)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    description = Column(Text)
    seo_id = Column(UUID(as_uuid=True), ForeignKey("seo_metadata.id", ondelete="SET NULL"))
    is_published = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    seo = relationship("SEOMetadata")
    properties = relationship("Property", back_populates="destination")
    packages = relationship("Package", back_populates="destination")

class SitePage(Base):
    __tablename__ = "site_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True)
    title = Column(String)
    body = Column(Text)
    blocks = Column(JSONB, default=[])
    seo_id = Column(UUID(as_uuid=True), ForeignKey("seo_metadata.id", ondelete="SET NULL"))
    is_published = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    seo = relationship("SEOMetadata")

class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_id = Column(UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="SET NULL"), index=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True, index=True)
    property_type = Column(String)
    address = Column(Text)
    contact_email = Column(String)
    contact_phone = Column(String)
    overview = Column(Text)
    rating = Column(Numeric(2, 1), default=0)
    is_published = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # New columns
    short_title = Column(String)
    starting_price = Column(Numeric(12, 2))
    recommended_days = Column(Integer)
    recommended_nights = Column(Integer)
    min_nights = Column(Integer)
    max_nights = Column(Integer)
    min_guests = Column(Integer)
    max_guests = Column(Integer)
    about = Column(Text)
    map_url = Column(Text)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    website_url = Column(String)
    reviews_count = Column(Integer, default=0)
    registration_status = Column(String, default='draft') # Enum PropertyRegistrationStatus
    registration_submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    registration_submitted_at = Column(Date) # Should be DateTime
    property_meta = Column(JSONB, default={})

    destination = relationship("Destination", back_populates="properties")
    assignments = relationship("PropertyAssignment", back_populates="property")
    room_types = relationship("RoomType", back_populates="property")
    rooms = relationship("Room", back_populates="property")
    property_amenities = relationship("PropertyAmenity", back_populates="property")
    property_policies = relationship("PropertyPolicy", back_populates="property")
    reviews = relationship("Review", back_populates="property")
    bookings = relationship("Booking", back_populates="property")
    nearby_places = relationship("NearbyPlace", back_populates="property")

class PropertyRegistrationStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class PropertyAssignment(Base):
    __tablename__ = "property_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assignment_role = Column(String, nullable=False) # 'property_admin','property_user','manager'
    scope = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    assigned_by = Column(UUID(as_uuid=True))
    revoked_by = Column(UUID(as_uuid=True))
    revoked_at = Column(Date) # Changed to Date as per schema implication or keep datetime if needed, but removing auto-timestamp
    notes = Column(Text)

    property = relationship("Property", back_populates="assignments")
    user = relationship("User", back_populates="property_assignments")

    __table_args__ = (UniqueConstraint('property_id', 'user_id', 'assignment_role', name='uq_property_assignment'),)

class RoomType(Base):
    __tablename__ = "room_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String)
    capacity = Column(Integer, nullable=False, default=2)
    base_tariff = Column(Numeric(12, 2), nullable=False, default=0)
    description = Column(Text)
    max_adults = Column(Integer, default=2)
    max_children = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)

    property = relationship("Property", back_populates="room_types")
    rooms = relationship("Room", back_populates="room_type")
    inventories = relationship("RoomInventory", back_populates="room_type")
    tariffs = relationship("RoomTariff", back_populates="room_type")
    blackout_dates = relationship("BlackoutDate", back_populates="room_type")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    room_type_id = Column(UUID(as_uuid=True), ForeignKey("room_types.id", ondelete="SET NULL"))
    room_number = Column(String)
    status = Column(String, default='available')
    is_deleted = Column(Boolean, default=False)

    property = relationship("Property", back_populates="rooms")
    room_type = relationship("RoomType", back_populates="rooms")

class RoomInventory(Base):
    __tablename__ = "room_inventories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_type_id = Column(UUID(as_uuid=True), ForeignKey("room_types.id", ondelete="CASCADE"), nullable=False)
    inventory_date = Column(Date, nullable=False)
    available_count = Column(Integer, nullable=False, default=0)
    is_blocked = Column(Boolean, default=False)
    note = Column(Text)
    updated_by = Column(UUID(as_uuid=True))

    room_type = relationship("RoomType", back_populates="inventories")

    __table_args__ = (UniqueConstraint('room_type_id', 'inventory_date', name='uq_room_inventory_date'),)

class RoomTariff(Base):
    __tablename__ = "room_tariffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_type_id = Column(UUID(as_uuid=True), ForeignKey("room_types.id", ondelete="CASCADE"), nullable=False)
    tariff_date = Column(Date, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, nullable=False, default='INR')
    min_stay = Column(Integer, default=1)
    created_by = Column(UUID(as_uuid=True))

    room_type = relationship("RoomType", back_populates="tariffs")

    __table_args__ = (UniqueConstraint('room_type_id', 'tariff_date', name='uq_room_tariff_date'),)

class BlackoutDate(Base):
    __tablename__ = "blackout_dates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_type_id = Column(UUID(as_uuid=True), ForeignKey("room_types.id", ondelete="CASCADE"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)

    room_type = relationship("RoomType", back_populates="blackout_dates")

class NearbyPlace(Base):
    __tablename__ = "nearby_places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    media_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="SET NULL"))
    distance_km = Column(Numeric(6, 2))
    order_index = Column(Integer, default=0)
    created_at = Column(Date, default=uuid.uuid4) # Placeholder, should be DateTime

    property = relationship("Property", back_populates="nearby_places")
    media = relationship("Media")
