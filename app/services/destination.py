from app.services.base import BaseService
from app.models.property import Destination
from app.schemas.property import DestinationCreate, DestinationUpdate

class DestinationService(BaseService[Destination, DestinationCreate, DestinationUpdate]):
    pass

destination_service = DestinationService(Destination)
