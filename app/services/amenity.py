from app.services.base import BaseService
from app.models.amenity import Amenity
from app.schemas.amenity import AmenityCreate, AmenityUpdate

class AmenityService(BaseService[Amenity, AmenityCreate, AmenityUpdate]):
    pass

amenity_service = AmenityService(Amenity)
