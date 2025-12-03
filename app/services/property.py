from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import BaseService
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate

class PropertyService(BaseService[Property, PropertyCreate, PropertyUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: PropertyCreate) -> Property:
        obj_in_data = obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # Prevent Pydantic from accessing unloaded relationship
        db_obj.destination = None 
        return db_obj

property_service = PropertyService(Property)
