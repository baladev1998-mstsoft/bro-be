# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.base import Base
from app.models.user import User, Role, Permission, RolePermission, UserRole
from app.models.property import (
    Property, PropertyAssignment, Destination, SEOMetadata, SitePage,
    RoomType, Room, RoomInventory, RoomTariff, BlackoutDate
)
from app.models.booking import Booking, BookingItem, Payment, BookingAddon
from app.models.media import Media, EntityMedia
from app.models.amenity import Amenity, AmenityOption, PropertyAmenity
from app.models.policy import Policy, PropertyPolicy
from app.models.package import Package, PackageItem, Itinerary, ItineraryDay
from app.models.review import Review
from app.models.offer import Offer
from app.models.cms import CMSPage, CMSPageTranslation, CMSSection, CMSSectionContent, CMSPageVersion
from app.models.audit import AuditLog, ActivityLog
from app.models.log import Log
from sqlalchemy.orm import configure_mappers

configure_mappers()
