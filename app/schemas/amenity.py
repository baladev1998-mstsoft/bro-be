from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# Amenity Option Schemas
class AmenityOptionBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    price: float = 0.0
    currency: str = "INR"
    meta: Optional[Dict[str, Any]] = None

class AmenityOptionCreate(AmenityOptionBase):
    amenity_id: UUID

class AmenityOptionUpdate(AmenityOptionBase):
    pass

class AmenityOption(AmenityOptionBase):
    id: UUID
    amenity_id: UUID
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Amenity Schemas
class AmenityBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    requires_configuration: bool = False
    is_chargeable: bool = False
    default_price: Optional[float] = None
    currency: str = "INR"
    meta: Optional[Dict[str, Any]] = None

class AmenityCreate(AmenityBase):
    pass

class AmenityUpdate(AmenityBase):
    pass

class Amenity(AmenityBase):
    id: UUID
    is_deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Property Amenity Schemas
class PropertyAmenityBase(BaseModel):
    enabled: bool = True
    is_chargeable: bool = False
    price: Optional[float] = None
    currency: str = "INR"
    apply_on: str = "per_stay"
    config: Optional[Dict[str, Any]] = None

class PropertyAmenityCreate(PropertyAmenityBase):
    property_id: UUID
    amenity_id: UUID

class PropertyAmenityUpdate(PropertyAmenityBase):
    pass

class PropertyAmenity(PropertyAmenityBase):
    id: UUID
    property_id: UUID
    amenity_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    amenity: Optional[Amenity] = None

    class Config:
        from_attributes = True
