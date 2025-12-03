from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.schemas.response import APIResponse, Meta

router = APIRouter()

@router.get("/", response_model=APIResponse[List[schemas.Booking]])
async def read_bookings(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.Booking).offset(skip).limit(limit))
    bookings = result.scalars().all()
    total = len(bookings)
    return APIResponse(
        success=True,
        message="Bookings fetched successfully",
        meta=Meta(limit=limit, offset=skip, total=total),
        data=bookings
    )

@router.post("/", response_model=APIResponse[schemas.Booking])
async def create_booking(
    *,
    db: AsyncSession = Depends(get_db),
    booking_in: schemas.BookingCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Placeholder
    pass
