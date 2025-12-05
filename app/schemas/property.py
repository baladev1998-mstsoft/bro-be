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
    
    # New fields
    short_title: Optional[str] = None
    starting_price: Optional[float] = None
    recommended_days: Optional[int] = None
    recommended_nights: Optional[int] = None
    min_nights: Optional[int] = None
    max_nights: Optional[int] = None
    min_guests: Optional[int] = None
    max_guests: Optional[int] = None
    about: Optional[str] = None
    map_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    website_url: Optional[str] = None
    property_meta: Optional[Dict[str, Any]] = {}

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
    
    reviews_count: Optional[int] = 0
    registration_status: Optional[str] = "draft"
    registration_submitted_by: Optional[UUID] = None
    registration_submitted_at: Optional[date] = None

    class Config:
        from_attributes = True

# Property Assignment Schemas
class PropertyAssignmentBase(BaseModel):
    user_id: UUID
    assignment_role: str
    scope: Optional[Dict[str, Any]] = {}
    is_active: bool = True
    notes: Optional[str] = None

class PropertyAssignmentCreate(PropertyAssignmentBase):
    pass

class PropertyAssignmentUpdate(PropertyAssignmentBase):
    pass

class PropertyAssignment(PropertyAssignmentBase):
    id: UUID
    property_id: UUID
    assigned_by: Optional[UUID] = None
    assigned_at: Optional[datetime] = None
    revoked_by: Optional[UUID] = None
    revoked_at: Optional[date] = None
    
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

# Nearby Place Schemas
class NearbyPlaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    distance_km: Optional[float] = None
    order_index: Optional[int] = 0

class NearbyPlaceCreate(NearbyPlaceBase):
    property_id: UUID
    media_id: Optional[UUID] = None

class NearbyPlaceUpdate(NearbyPlaceBase):
    media_id: Optional[UUID] = None

class NearbyPlace(NearbyPlaceBase):
    id: UUID
    property_id: UUID
    media_id: Optional[UUID] = None
    created_at: Optional[date] = None
    
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

# Public API Schemas
class AmenityPublic(BaseModel):
    id: UUID
    image: Optional[str] = None
    number: Optional[int] = None
    label: str

class NearbyPlacePublic(BaseModel):
    id: UUID
    image: Optional[str] = None
    name: str
    description: Optional[str] = None

class RulePublic(BaseModel):
    header: str
    description: Optional[str] = None

class PropertyPublicDetail(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    price: Optional[str] = None
    rating: Optional[str] = None
    reviews: Optional[str] = None
    days: Optional[int] = None
    nights: Optional[int] = None
    guests: Optional[str] = None
    location: Optional[str] = None
    property_image: Optional[str] = None
    images: List[str] = []
    about: Optional[str] = None
    amenities: List[AmenityPublic] = []
    map_location: Optional[str] = None
    nearby_attractions: List[NearbyPlacePublic] = []
    rules: List[RulePublic] = []
    page_route: str
    suggestions: Optional[str] = None

    class Config:
        from_attributes = True
