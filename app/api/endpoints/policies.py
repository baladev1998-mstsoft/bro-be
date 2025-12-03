from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import services, schemas, models
from app.api import deps
from app.db.session import get_db
from app.schemas.response import APIResponse, Meta

router = APIRouter()

@router.get("/", response_model=APIResponse[List[schemas.Policy]])
async def read_policies(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve policies.
    """
    policies = await services.policy_service.get_multi(db, skip=skip, limit=limit)
    total = len(policies)
    return APIResponse(
        success=True,
        message="Policies fetched successfully",
        meta=Meta(limit=limit, offset=skip, total=total),
        data=policies
    )

@router.post("/", response_model=APIResponse[schemas.Policy])
async def create_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_in: schemas.PolicyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new policy.
    """
    policy = await services.policy_service.create(db=db, obj_in=policy_in)
    return APIResponse(
        success=True,
        message="Policy created successfully",
        data=policy
    )
