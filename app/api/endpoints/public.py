from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import aliased
from app import models, schemas
from app.db.session import get_db
from app.schemas.response import APIResponse, Meta
import uuid

router = APIRouter()

@router.get("/destinations", response_model=APIResponse[List[schemas.DestinationPublic]])
async def read_public_destinations(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve published destinations with their primary image.
    """
    # Alias for EntityMedia and Media to avoid confusion if we join multiple times (though simple here)
    em = aliased(models.EntityMedia)
    m = aliased(models.Media)

    stmt = (
        select(models.Destination, m.url)
        .outerjoin(
            em,
            and_(
                em.entity_id == models.Destination.id,
                em.entity_type == "destination",
                em.is_primary == True
            )
        )
        .outerjoin(m, m.id == em.media_id)
        .where(models.Destination.is_published == True)
        .where(models.Destination.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data = []
    for dest, image_url in rows:
        data.append(schemas.DestinationPublic(
            id=dest.id,
            name=dest.name,
            image_url=image_url
        ))

    return APIResponse(
        success=True,
        message="Destinations fetched successfully",
        meta=Meta(limit=limit, offset=skip, total=len(data)),
        data=data
    )

@router.get("/destinations/{destination_id}/properties", response_model=APIResponse[List[schemas.PropertyPublic]])
async def read_public_properties_by_destination(
    destination_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve published properties for a specific destination with their primary image.
    """
    # Check if destination exists and is published
    dest_stmt = select(models.Destination).where(
        models.Destination.id == destination_id,
        models.Destination.is_published == True,
        models.Destination.is_deleted == False
    )
    dest_result = await db.execute(dest_stmt)
    if not dest_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Destination not found")

    em = aliased(models.EntityMedia)
    m = aliased(models.Media)

    stmt = (
        select(models.Property, m.url)
        .outerjoin(
            em,
            and_(
                em.entity_id == models.Property.id,
                em.entity_type == "property",
                em.is_primary == True
            )
        )
        .outerjoin(m, m.id == em.media_id)
        .where(models.Property.destination_id == destination_id)
        .where(models.Property.is_published == True)
        .where(models.Property.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data = []
    for prop, image_url in rows:
        data.append(schemas.PropertyPublic(
            id=prop.id,
            name=prop.name,
            image_url=image_url
        ))

    return APIResponse(
        success=True,
        message="Properties fetched successfully",
        meta=Meta(limit=limit, offset=skip, total=len(data)),
        data=data
    )
