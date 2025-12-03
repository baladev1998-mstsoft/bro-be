from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app import models, schemas, services
from app.api import deps
from app.db.session import get_db
from app.schemas.response import APIResponse, Meta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[schemas.Property], dependencies=[Depends(deps.PermissionChecker("PROPERTY_READ"))])
async def read_properties(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(
        select(models.Property)
        .options(selectinload(models.Property.destination))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/", response_model=schemas.Property, dependencies=[Depends(deps.PermissionChecker("PROPERTY_CREATE"))])
async def create_property(
    *,
    db: AsyncSession = Depends(get_db),
    property_in: schemas.PropertyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    property = await services.property_service.create(db=db, obj_in=property_in)
    return property
