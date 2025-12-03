from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# Package Item Schemas
class PackageItemBase(BaseModel):
    item_type: str
    item_ref: Optional[UUID] = None
    day: int = 1
    description: Optional[str] = None

class PackageItemCreate(PackageItemBase):
    package_id: UUID

class PackageItemUpdate(PackageItemBase):
    pass

class PackageItem(PackageItemBase):
    id: UUID
    package_id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Package Schemas
class PackageBase(BaseModel):
    title: str
    slug: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    duration_days: Optional[int] = None
    inclusions: Optional[str] = None
    exclusions: Optional[str] = None
    is_published: bool = False

class PackageCreate(PackageBase):
    destination_id: Optional[UUID] = None

class PackageUpdate(PackageBase):
    pass

class Package(PackageBase):
    id: UUID
    destination_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[PackageItem] = []

    class Config:
        from_attributes = True

# Itinerary Day Schemas
class ItineraryDayBase(BaseModel):
    day: int
    title: Optional[str] = None
    details: Optional[str] = None

class ItineraryDayCreate(ItineraryDayBase):
    itinerary_id: UUID

class ItineraryDayUpdate(ItineraryDayBase):
    pass

class ItineraryDay(ItineraryDayBase):
    id: UUID
    itinerary_id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Itinerary Schemas
class ItineraryBase(BaseModel):
    title: str
    slug: Optional[str] = None
    duration_days: Optional[int] = None
    description: Optional[str] = None

class ItineraryCreate(ItineraryBase):
    pass

class ItineraryUpdate(ItineraryBase):
    pass

class Itinerary(ItineraryBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    days: List[ItineraryDay] = []

    class Config:
        from_attributes = True
