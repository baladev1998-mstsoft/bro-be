from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, Field, HttpUrl

# Shared / Base Schemas
class SEOMetadataBase(BaseModel):
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    canonical_url: Optional[str] = None
    robots: Optional[str] = None

class SEOMetadataCreate(SEOMetadataBase):
    pass

class SEOMetadataUpdate(SEOMetadataBase):
    pass

class SEOMetadata(SEOMetadataBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Destination Schemas
class DestinationBase(BaseModel):
    name: str
    slug: str
    country: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    is_published: Optional[bool] = False

class DestinationCreate(DestinationBase):
    pass

class DestinationUpdate(DestinationBase):
    name: Optional[str] = None
    slug: Optional[str] = None

class Destination(DestinationBase):
    id: UUID
    seo_id: Optional[UUID] = None
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    seo: Optional[SEOMetadata] = None

    class Config:
        from_attributes = True

# Property Schemas
class PropertyBase(BaseModel):
    name: str
    slug: str
    property_type: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    overview: Optional[str] = None
    rating: Optional[float] = 0.0
    is_published: Optional[bool] = False

class PropertyCreate(PropertyBase):
    destination_id: Optional[UUID] = None

class PropertyUpdate(PropertyBase):
    name: Optional[str] = None
    slug: Optional[str] = None

class Property(PropertyBase):
    id: UUID
    destination_id: Optional[UUID] = None
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    destination: Optional[Destination] = None

    class Config:
        from_attributes = True

# Room Type Schemas
class RoomTypeBase(BaseModel):
    name: str
    slug: Optional[str] = None
    capacity: int = 2
    base_tariff: float = 0.0
    description: Optional[str] = None
    max_adults: int = 2
    max_children: int = 0

class RoomTypeCreate(RoomTypeBase):
    property_id: UUID

class RoomTypeUpdate(RoomTypeBase):
    name: Optional[str] = None

class RoomType(RoomTypeBase):
    id: UUID
    property_id: UUID
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Room Schemas
class RoomBase(BaseModel):
    room_number: Optional[str] = None
    status: str = "available"

class RoomCreate(RoomBase):
    property_id: UUID
    room_type_id: Optional[UUID] = None

class RoomUpdate(RoomBase):
    pass

class Room(RoomBase):
    id: UUID
    property_id: UUID
    room_type_id: Optional[UUID] = None
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Inventory Schemas
class RoomInventoryBase(BaseModel):
    inventory_date: date
    available_count: int = 0
    is_blocked: bool = False
    note: Optional[str] = None

class RoomInventoryCreate(RoomInventoryBase):
    room_type_id: UUID

class RoomInventoryUpdate(RoomInventoryBase):
    inventory_date: Optional[date] = None

class RoomInventory(RoomInventoryBase):
    id: UUID
    room_type_id: UUID
    updated_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Tariff Schemas
class RoomTariffBase(BaseModel):
    tariff_date: date
    price: float
    currency: str = "INR"
    min_stay: int = 1

class RoomTariffCreate(RoomTariffBase):
    room_type_id: UUID

class RoomTariffUpdate(RoomTariffBase):
    tariff_date: Optional[date] = None
    price: Optional[float] = None

class RoomTariff(RoomTariffBase):
    id: UUID
    room_type_id: UUID
    created_by: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
