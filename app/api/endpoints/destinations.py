from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import services, schemas, models
from app.api import deps
from app.db.session import get_db
from app.schemas.response import APIResponse, Meta

router = APIRouter()

@router.get("/", response_model=APIResponse[List[schemas.Destination]])
async def read_destinations(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve destinations.
    """
    destinations = await services.destination_service.get_multi(db, skip=skip, limit=limit)
    total = len(destinations)
    return APIResponse(
        success=True,
        message="Destinations fetched successfully",
        meta=Meta(limit=limit, offset=skip, total=total),
        data=destinations
    )

@router.post("/", response_model=APIResponse[schemas.Destination])
async def create_destination(
    *,
    db: AsyncSession = Depends(get_db),
    destination_in: schemas.DestinationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new destination.
    """
    destination = await services.destination_service.create(db=db, obj_in=destination_in)
    return APIResponse(
        success=True,
        message="Destination created successfully",
        data=destination
    )
