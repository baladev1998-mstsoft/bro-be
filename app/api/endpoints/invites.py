from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.schemas.invitation import InvitationCreate, InvitationResponse, InvitationAccept
from app.models.invitation import InvitationToken
from app.models.user import User, UserRole, Role
from app.models.property import PropertyAssignment
from app.api.deps import get_current_user
from app.core.security import get_password_hash, create_access_token
from app.core.config import settings
from datetime import datetime, timedelta, timezone
import secrets
import uuid

from app.schemas.response import APIResponse

router = APIRouter()

@router.post("/", response_model=APIResponse[InvitationResponse])
async def create_invitation(
    invite_in: InvitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: Check if current_user is SYSTEM_ADMIN or has permission to invite
    # For now, assuming only SYSTEM_ADMIN can invite or we skip check for MVP if not strictly enforced yet
    
    # Generate token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=invite_in.expires_in_minutes)
    
    invitation = InvitationToken(
        email=invite_in.email,
        token=token,
        role=invite_in.role,
        property_id=invite_in.property_id,
        invited_by=current_user.id,
        message=invite_in.message,
        expires_at=expires_at
    )
    
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    
    # TODO: Send email/SMS
    print(f"Invitation link: {settings.API_V1_STR}/invites/accept?token={token}")
    
    return APIResponse(
        success=True,
        message="Invitation created successfully",
        data=InvitationResponse(token=token, expires_at=expires_at)
    )

@router.post("/accept", response_model=APIResponse[dict])
async def accept_invitation(
    accept_in: InvitationAccept,
    db: AsyncSession = Depends(get_db),
):
    # Verify token
    result = await db.execute(select(InvitationToken).where(InvitationToken.token == accept_in.token))
    invitation = result.scalars().first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid token")
    
    if invitation.accepted:
        raise HTTPException(status_code=400, detail="Invitation already accepted")
        
    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invitation expired")
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == invitation.email))
    user = result.scalars().first()
    
    if not user:
        # Create user
        user = User(
            email=invitation.email,
            full_name=accept_in.full_name,
            password_hash=get_password_hash(accept_in.password),
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Assign role
    # Find role by name
    result = await db.execute(select(Role).where(Role.name == invitation.role))
    role = result.scalars().first()
    
    if role:
        # Check if user already has this role
        result = await db.execute(select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id))
        existing_role = result.scalars().first()
        if not existing_role:
            user_role = UserRole(user_id=user.id, role_id=role.id)
            db.add(user_role)
    
    # If property_id is present, assign property assignment
    if invitation.property_id:
        assignment = PropertyAssignment(
            property_id=invitation.property_id,
            user_id=user.id,
            assignment_role=invitation.role, # Using the same role name for assignment role for now
            assigned_by=invitation.invited_by
        )
        db.add(assignment)
    
    # Mark invitation as accepted
    invitation.accepted = True
    invitation.accepted_by = user.id
    invitation.accepted_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    # Generate auth token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return APIResponse(
        success=True,
        message="Invitation accepted successfully",
        data={"access_token": access_token, "token_type": "bearer"}
    )
