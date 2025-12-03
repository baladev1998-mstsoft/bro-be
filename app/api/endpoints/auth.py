from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app import schemas, models
from app.schemas.response import APIResponse
from app.core import security
from app.core.config import settings
from app.db.session import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

async def authenticate_user(db: AsyncSession, username: str, password: str):
    # Check if username is email or phone
    query = select(models.User).where(
        or_(
            models.User.email == username,
            models.User.phone == username
        )
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        return None
    if not security.verify_password(password, user.password_hash):
        return None
    return user

@router.post("/login", response_model=schemas.LoginResponse)
async def login(
    db: AsyncSession = Depends(get_db),
    login_data: schemas.Login = Body(...),
) -> Any:
    """
    JSON Login for Frontend.
    """
    user = await authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email/phone or password",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Fetch roles and user_roles for scope
    stmt = select(models.User).options(
        selectinload(models.User.roles)
    ).where(models.User.id == user.id)
    result = await db.execute(stmt)
    user_with_roles = result.scalars().first()
    
    # Fetch UserRole association to get scope
    # This is a bit tricky with the current relationship setup in User model
    # We need to query UserRole directly to get the scope for each role
    stmt_ur = select(models.UserRole).where(models.UserRole.user_id == user.id)
    result_ur = await db.execute(stmt_ur)
    user_roles_assoc = result_ur.scalars().all()
    
    role_scope_map = {ur.role_id: ur.scope for ur in user_roles_assoc}
    
    roles_data = []
    for role in user_with_roles.roles:
        scope_data = role_scope_map.get(role.id, {})
        # Assuming scope is stored as JSON, we might need to format it as string or keep as dict
        # The requirement says scope: "global" or "tenant:uuid"
        # For now, let's assume the 'scope' column in UserRole holds this string or a dict we convert
        # If it's a dict like {"tenant_id": "..."} we need to parse it.
        # Let's assume for now it's a simple string in the JSON or we default to "global"
        
        scope_str = "global"
        if scope_data and isinstance(scope_data, dict):
             # Example logic: if tenant_id is present, use it
             if "tenant_id" in scope_data:
                 scope_str = f"tenant:{scope_data['tenant_id']}"
             elif "scope" in scope_data:
                 scope_str = scope_data["scope"]
        
        roles_data.append({"role": role.name, "scope": scope_str})

    # Determine default tenant
    default_tenant = None
    # Logic to find default tenant, e.g., from property assignments
    # For now, leaving as None or first tenant scope found
    for r in roles_data:
        if r["scope"].startswith("tenant:"):
            default_tenant = r["scope"].split(":")[1]
            break

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "name": user.full_name,
        "roles": roles_data,
        "default_tenant": default_tenant,
        "type": "access"
    }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires, claims=token_payload
    )
    
    refresh_token = security.create_refresh_token(user.id)
    
    return {
        "meta": {
            "success": True,
            "message": "Login successful"
        },
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "roles": roles_data,
                "default_tenant": default_tenant
            }
        },
        "error": None
    }

@router.post("/refresh", response_model=schemas.LoginResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Refresh access token.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )
        
    user = await db.get(models.User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # Re-fetch roles and scope logic (duplicated from login for now, should be refactored to a service)
    stmt = select(models.User).options(
        selectinload(models.User.roles)
    ).where(models.User.id == user.id)
    result = await db.execute(stmt)
    user_with_roles = result.scalars().first()
    
    stmt_ur = select(models.UserRole).where(models.UserRole.user_id == user.id)
    result_ur = await db.execute(stmt_ur)
    user_roles_assoc = result_ur.scalars().all()
    
    role_scope_map = {ur.role_id: ur.scope for ur in user_roles_assoc}
    
    roles_data = []
    for role in user_with_roles.roles:
        scope_data = role_scope_map.get(role.id, {})
        scope_str = "global"
        if scope_data and isinstance(scope_data, dict):
             if "tenant_id" in scope_data:
                 scope_str = f"tenant:{scope_data['tenant_id']}"
             elif "scope" in scope_data:
                 scope_str = scope_data["scope"]
        roles_data.append({"role": role.name, "scope": scope_str})

    default_tenant = None
    for r in roles_data:
        if r["scope"].startswith("tenant:"):
            default_tenant = r["scope"].split(":")[1]
            break

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "name": user.full_name,
        "roles": roles_data,
        "default_tenant": default_tenant,
        "type": "access"
    }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires, claims=token_payload
    )
    
    # Optionally rotate refresh token here
    
    return {
        "meta": {
            "success": True,
            "message": "Token refreshed successfully"
        },
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token, # Return same refresh token or rotate
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "roles": roles_data,
                "default_tenant": default_tenant
            }
        },
        "error": None
    }

@router.post("/access-token", response_model=APIResponse[schemas.Token])
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 Form Login for Swagger UI.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email/phone or password",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Fetch roles and permissions
    stmt = select(models.User).options(
        selectinload(models.User.roles).selectinload(models.Role.permissions)
    ).where(models.User.id == user.id)
    result = await db.execute(stmt)
    user_with_roles = result.scalars().first()
    
    roles = [role.name for role in user_with_roles.roles]
    permissions = set()
    for role in user_with_roles.roles:
        for perm in role.permissions:
            permissions.add(perm.code)
            
    scope = {}
    
    claims = {
        "roles": roles,
        "permissions": list(permissions),
        "scope": scope
    }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires, claims=claims
        ),
        "token_type": "bearer",
    }

@router.post("/decode-token", response_model=schemas.TokenPayload)
async def decode_token(
    token: str = Body(..., embed=True),
) -> Any:
    """
    Decode a JWT token and return its claims.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return payload
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid token: {str(e)}",
        )
