from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel
from app.models.booking import BookingStatus

# Booking Item Schemas
class BookingItemBase(BaseModel):
    check_in: date
    check_out: date
    nights: int
    qty: int = 1
    price_per_night: float
    total_price: float

class BookingItemCreate(BookingItemBase):
    room_type_id: Optional[UUID] = None

class BookingItemUpdate(BookingItemBase):
    pass

class BookingItem(BookingItemBase):
    id: UUID
    booking_id: UUID
    room_type_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Booking Addon Schemas
class BookingAddonBase(BaseModel):
    name: str
    price: float = 0.0
    currency: str = "INR"
    qty: int = 1
    total_price: float = 0.0
    notes: Optional[str] = None

class BookingAddonCreate(BookingAddonBase):
    amenity_id: Optional[UUID] = None
    amenity_option_id: Optional[UUID] = None
    property_amenity_id: Optional[UUID] = None

class BookingAddonUpdate(BookingAddonBase):
    pass

class BookingAddon(BookingAddonBase):
    id: UUID
    booking_id: UUID
    amenity_id: Optional[UUID] = None
    amenity_option_id: Optional[UUID] = None
    property_amenity_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    amount: float
    currency: str = "INR"
    payment_method: Optional[str] = None
    payment_provider: Optional[str] = None
    status: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None

class PaymentCreate(PaymentBase):
    booking_id: Optional[UUID] = None

class PaymentUpdate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: UUID
    booking_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    total_amount: float = 0.0
    currency: str = "INR"
    status: BookingStatus = BookingStatus.PENDING
    booking_reference: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class BookingCreate(BookingBase):
    user_id: Optional[UUID] = None
    property_id: Optional[UUID] = None
    items: Optional[List[BookingItemCreate]] = []
    addons: Optional[List[BookingAddonCreate]] = []

class BookingUpdate(BookingBase):
    pass

class Booking(BookingBase):
    id: UUID
    user_id: Optional[UUID] = None
    property_id: Optional[UUID] = None
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    booking_items: List[BookingItem] = []
    payments: List[Payment] = []
    addons: List[BookingAddon] = []

    class Config:
        from_attributes = True
