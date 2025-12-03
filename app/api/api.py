from fastapi import APIRouter
from app.api.endpoints import auth, users, properties, bookings, amenities, policies, destinations, cms, public

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(amenities.router, prefix="/amenities", tags=["amenities"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(destinations.router, prefix="/destinations", tags=["destinations"])
api_router.include_router(cms.router, prefix="/cms", tags=["cms"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
