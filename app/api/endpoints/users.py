from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.schemas.response import APIResponse, Meta

router = APIRouter()

@router.get("/", response_model=APIResponse[List[schemas.User]])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    total = len(users)
    return APIResponse(
        success=True,
        message="Users fetched successfully",
        meta=Meta(limit=limit, offset=skip, total=total),
        data=users
    )

@router.get("/me", response_model=APIResponse[schemas.User])
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    return APIResponse(
        success=True,
        message="User details fetched successfully",
        data=current_user
    )
