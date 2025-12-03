from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy import select
from sqlalchemy.orm import selectinload

security_scheme = HTTPBearer()

async def get_token_payload(
    token: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_payload: schemas.TokenPayload = Depends(get_token_payload)
) -> models.User:
    result = await db.execute(select(models.User).where(models.User.id == token_payload.sub))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(
        self, 
        payload: schemas.TokenPayload = Depends(get_token_payload),
        db: AsyncSession = Depends(get_db)
    ):
        # Extract role names from payload
        # payload.roles is now a list of RoleScope objects
        role_names = [r.role for r in payload.roles]
        
        # System Admin has all permissions
        if "SYSTEM_ADMIN" in role_names:
            return True
            
        # Fetch roles and their permissions from DB
        stmt = select(models.Role).options(
            selectinload(models.Role.permissions)
        ).where(models.Role.name.in_(role_names))
        
        result = await db.execute(stmt)
        roles_db = result.scalars().all()
        
        user_permissions = set()
        for role in roles_db:
            for perm in role.permissions:
                user_permissions.add(perm.code)
                
        if self.required_permission in user_permissions:
            return True
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions. Required: {self.required_permission}"
        )
