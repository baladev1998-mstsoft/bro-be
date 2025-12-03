from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class DestinationPublic(BaseModel):
    id: UUID
    name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class PropertyPublic(BaseModel):
    id: UUID
    name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
