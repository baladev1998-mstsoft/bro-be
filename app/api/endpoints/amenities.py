from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import services, schemas, models
from app.api import deps
from app.db.session import get_db
from app.schemas.response import APIResponse, Meta

router = APIRouter()

@router.get("/", response_model=APIResponse[List[schemas.Amenity]])
async def read_amenities(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve amenities.
    """
    amenities = await services.amenity_service.get_multi(db, skip=skip, limit=limit)
    total = len(amenities) # Should be count query
    return APIResponse(
        success=True,
        message="Amenities fetched successfully",
        meta=Meta(limit=limit, offset=skip, total=total),
        data=amenities
    )

@router.post("/", response_model=APIResponse[schemas.Amenity])
async def create_amenity(
    *,
    db: AsyncSession = Depends(get_db),
    amenity_in: schemas.AmenityCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new amenity.
    """
    amenity = await services.amenity_service.create(db=db, obj_in=amenity_in)
    return APIResponse(
        success=True,
        message="Amenity created successfully",
        data=amenity
    )
