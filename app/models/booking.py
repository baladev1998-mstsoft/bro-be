import uuid
import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Integer, Date, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    NO_SHOW = "no_show"
    REFUNDED = "refunded"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="SET NULL"), index=True)
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    currency = Column(String, default='INR')
    status = Column(String, default=BookingStatus.PENDING)
    booking_reference = Column(String, unique=True)
    contact_name = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    meta = Column(JSONB, default={})
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="bookings")
    property = relationship("Property", back_populates="bookings")
    booking_items = relationship("BookingItem", back_populates="booking")
    payments = relationship("Payment", back_populates="booking")
    addons = relationship("BookingAddon", back_populates="booking")
    reviews = relationship("Review", back_populates="booking")

class BookingItem(Base):
    __tablename__ = "booking_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    room_type_id = Column(UUID(as_uuid=True), ForeignKey("room_types.id", ondelete="SET NULL"))
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    nights = Column(Integer, nullable=False)
    qty = Column(Integer, nullable=False, default=1)
    price_per_night = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)

    booking = relationship("Booking", back_populates="booking_items")
    room_type = relationship("RoomType")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"))
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, nullable=False, default='INR')
    payment_method = Column(String)
    payment_provider = Column(String)
    status = Column(String)
    provider_response = Column(JSONB)

    booking = relationship("Booking", back_populates="payments")

class BookingAddon(Base):
    __tablename__ = "booking_addons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    amenity_id = Column(UUID(as_uuid=True), ForeignKey("amenities.id", ondelete="SET NULL"))
    amenity_option_id = Column(UUID(as_uuid=True), ForeignKey("amenity_options.id", ondelete="SET NULL"))
    property_amenity_id = Column(UUID(as_uuid=True), ForeignKey("property_amenities.id", ondelete="SET NULL"))
    name = Column(String, nullable=False)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    currency = Column(String, default='INR')
    qty = Column(Integer, default=1)
    total_price = Column(Numeric(12, 2), nullable=False, default=0)
    notes = Column(Text)

    booking = relationship("Booking", back_populates="addons")
    amenity = relationship("Amenity")
    amenity_option = relationship("AmenityOption")
    property_amenity = relationship("PropertyAmenity")
