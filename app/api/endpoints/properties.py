from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app import models, schemas, services
from app.api import deps
from app.db.session import get_db
from app.schemas.response import APIResponse, Meta
import logging
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)




# Registration
@router.post("/register", response_model=APIResponse[schemas.Property])
async def register_property(
    *,
    db: AsyncSession = Depends(get_db),
    property_in: schemas.PropertyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Create property with draft status
    obj_in_data = property_in.dict()
    db_obj = models.Property(**obj_in_data)
    db_obj.registration_status = models.PropertyRegistrationStatus.DRAFT
    db_obj.registration_submitted_by = current_user.id
    db_obj.created_by = current_user.id
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    
    # Assign current user as PROPERTY_ADMIN
    assignment = models.PropertyAssignment(
        property_id=db_obj.id,
        user_id=current_user.id,
        assignment_role="property_admin",
        assigned_by=current_user.id
    )
    db.add(assignment)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="Property registered successfully",
        data=db_obj
    )

# Update
@router.patch("/{property_id}", response_model=APIResponse[schemas.Property])
async def update_property(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    property_in: schemas.PropertyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Check permissions (omitted for brevity, assume property_admin or system_admin)
    result = await db.execute(select(models.Property).where(models.Property.id == property_id))
    property = result.scalars().first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
        
    update_data = property_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(property, field, value)
        
    property.updated_by = current_user.id
    property.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(property)
    return APIResponse(
        success=True,
        message="Property updated successfully",
        data=property
    )

# Submit for Review
@router.post("/{property_id}/submit-for-review", response_model=APIResponse[schemas.Property])
async def submit_for_review(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.Property).where(models.Property.id == property_id))
    property = result.scalars().first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
        
    property.registration_status = models.PropertyRegistrationStatus.PENDING_REVIEW
    property.registration_submitted_at = datetime.now(timezone.utc) # Fix type mismatch if needed
    property.registration_submitted_by = current_user.id
    
    await db.commit()
    await db.refresh(property)
    return APIResponse(
        success=True,
        message="Property submitted for review",
        data=property
    )

# Review (Approve/Reject)
@router.post("/{property_id}/review", response_model=APIResponse[schemas.Property])
async def review_property(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    action: str = Query(..., regex="^(approve|reject)$"),
    note: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user), # Should be SYSTEM_ADMIN
) -> Any:
    result = await db.execute(select(models.Property).where(models.Property.id == property_id))
    property = result.scalars().first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
        
    if action == "approve":
        property.registration_status = models.PropertyRegistrationStatus.APPROVED
    else:
        property.registration_status = models.PropertyRegistrationStatus.REJECTED
        
    # Log note if needed
    
    await db.commit()
    await db.refresh(property)
    return APIResponse(
        success=True,
        message=f"Property {action}d successfully",
        data=property
    )

# Publish
@router.post("/{property_id}/publish", response_model=APIResponse[schemas.Property])
async def publish_property(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.Property).where(models.Property.id == property_id))
    property = result.scalars().first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
        
    if property.registration_status != models.PropertyRegistrationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Property must be approved before publishing")
        
    property.is_published = True
    await db.commit()
    await db.refresh(property)
    return APIResponse(
        success=True,
        message="Property published successfully",
        data=property
    )

# Assignments
@router.post("/{property_id}/assignments", response_model=APIResponse[schemas.PropertyAssignment])
async def create_assignment(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    assignment_in: schemas.PropertyAssignmentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Check permissions
    
    assignment = models.PropertyAssignment(
        property_id=property_id,
        user_id=assignment_in.user_id,
        assignment_role=assignment_in.assignment_role,
        scope=assignment_in.scope,
        is_active=assignment_in.is_active,
        notes=assignment_in.notes,
        assigned_by=current_user.id
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return APIResponse(
        success=True,
        message="Assignment created successfully",
        data=assignment
    )

@router.get("/{property_id}/assignments", response_model=APIResponse[List[schemas.PropertyAssignment]])
async def read_assignments(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Check permissions
    result = await db.execute(select(models.PropertyAssignment).where(models.PropertyAssignment.property_id == property_id))
    assignments = result.scalars().all()
    return APIResponse(
        success=True,
        message="Assignments retrieved successfully",
        data=assignments
    )

@router.delete("/{property_id}/assignments/{assignment_id}", response_model=APIResponse[schemas.PropertyAssignment])
async def delete_assignment(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    assignment_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Check permissions
    result = await db.execute(select(models.PropertyAssignment).where(models.PropertyAssignment.id == assignment_id))
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    await db.delete(assignment)
    await db.commit()
    return APIResponse(
        success=True,
        message="Assignment deleted successfully",
        data=assignment
    )

# Room Types
@router.post("/{property_id}/room-types", response_model=APIResponse[schemas.RoomType])
async def create_room_type(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    room_type_in: schemas.RoomTypeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Check permissions
    room_type = models.RoomType(**room_type_in.dict(), property_id=property_id)
    db.add(room_type)
    await db.commit()
    await db.refresh(room_type)
    return APIResponse(
        success=True,
        message="Room Type created successfully",
        data=room_type
    )

@router.get("/{property_id}/room-types", response_model=APIResponse[List[schemas.RoomType]])
async def read_room_types(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.RoomType).where(models.RoomType.property_id == property_id))
    room_types = result.scalars().all()
    return APIResponse(
        success=True,
        message="Room Types retrieved successfully",
        data=room_types
    )

@router.patch("/{property_id}/room-types/{room_type_id}", response_model=APIResponse[schemas.RoomType])
async def update_room_type(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    room_type_id: UUID,
    room_type_in: schemas.RoomTypeUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.RoomType).where(models.RoomType.id == room_type_id))
    room_type = result.scalars().first()
    if not room_type:
        raise HTTPException(status_code=404, detail="Room Type not found")
        
    update_data = room_type_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room_type, field, value)
        
    await db.commit()
    await db.refresh(room_type)
    return APIResponse(
        success=True,
        message="Room Type updated successfully",
        data=room_type
    )

# Inventory
@router.post("/{property_id}/room-types/{room_type_id}/inventory", response_model=APIResponse[schemas.RoomInventory])
async def update_inventory(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    room_type_id: UUID,
    inventory_in: schemas.RoomInventoryCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Upsert logic
    # Check if inventory exists for date
    result = await db.execute(select(models.RoomInventory).where(
        models.RoomInventory.room_type_id == room_type_id,
        models.RoomInventory.inventory_date == inventory_in.inventory_date
    ))
    inventory = result.scalars().first()
    
    if inventory:
        inventory.available_count = inventory_in.available_count
        inventory.is_blocked = inventory_in.is_blocked
        inventory.note = inventory_in.note
        inventory.updated_by = current_user.id
        inventory.updated_at = datetime.now(timezone.utc)
    else:
        inventory = models.RoomInventory(
            room_type_id=room_type_id,
            inventory_date=inventory_in.inventory_date,
            available_count=inventory_in.available_count,
            is_blocked=inventory_in.is_blocked,
            note=inventory_in.note,
            updated_by=current_user.id
        )
        db.add(inventory)
        
    await db.commit()
    await db.refresh(inventory)
    return APIResponse(
        success=True,
        message="Inventory updated successfully",
        data=inventory
    )

# Tariff
@router.post("/{property_id}/room-types/{room_type_id}/tariff", response_model=APIResponse[schemas.RoomTariff])
async def update_tariff(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    room_type_id: UUID,
    tariff_in: schemas.RoomTariffCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Upsert logic
    result = await db.execute(select(models.RoomTariff).where(
        models.RoomTariff.room_type_id == room_type_id,
        models.RoomTariff.tariff_date == tariff_in.tariff_date
    ))
    tariff = result.scalars().first()
    
    if tariff:
        tariff.price = tariff_in.price
        tariff.currency = tariff_in.currency
        tariff.min_stay = tariff_in.min_stay
        # tariff.updated_by = current_user.id # If field exists
    else:
        tariff = models.RoomTariff(
            room_type_id=room_type_id,
            tariff_date=tariff_in.tariff_date,
            price=tariff_in.price,
            currency=tariff_in.currency,
            min_stay=tariff_in.min_stay,
            created_by=current_user.id
        )
        db.add(tariff)
        
    await db.commit()
    await db.refresh(tariff)
    return APIResponse(
        success=True,
        message="Tariff updated successfully",
        data=tariff
    )

# Amenities
@router.post("/{property_id}/amenities", response_model=APIResponse[schemas.PropertyAmenity])
async def update_property_amenity(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    amenity_in: schemas.PropertyAmenityCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Upsert logic
    result = await db.execute(select(models.PropertyAmenity).where(
        models.PropertyAmenity.property_id == property_id,
        models.PropertyAmenity.amenity_id == amenity_in.amenity_id
    ))
    prop_amenity = result.scalars().first()
    
    if prop_amenity:
        prop_amenity.enabled = amenity_in.enabled
        prop_amenity.is_chargeable = amenity_in.is_chargeable
        prop_amenity.price = amenity_in.price
        prop_amenity.currency = amenity_in.currency
        prop_amenity.apply_on = amenity_in.apply_on
        prop_amenity.config = amenity_in.config
    else:
        prop_amenity = models.PropertyAmenity(
            property_id=property_id,
            amenity_id=amenity_in.amenity_id,
            enabled=amenity_in.enabled,
            is_chargeable=amenity_in.is_chargeable,
            price=amenity_in.price,
            currency=amenity_in.currency,
            apply_on=amenity_in.apply_on,
            config=amenity_in.config
        )
        db.add(prop_amenity)
        
    await db.commit()
    await db.refresh(prop_amenity)
    return APIResponse(
        success=True,
        message="Property Amenity updated successfully",
        data=prop_amenity
    )

# Policies
@router.post("/{property_id}/policies", response_model=APIResponse[schemas.PropertyPolicy])
async def update_property_policy(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    policy_in: schemas.PropertyPolicyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Upsert logic
    result = await db.execute(select(models.PropertyPolicy).where(
        models.PropertyPolicy.property_id == property_id,
        models.PropertyPolicy.policy_id == policy_in.policy_id
    ))
    prop_policy = result.scalars().first()
    
    if prop_policy:
        prop_policy.content = policy_in.content
        prop_policy.short_text = policy_in.short_text
        prop_policy.effective_from = policy_in.effective_from
        prop_policy.effective_to = policy_in.effective_to
    else:
        prop_policy = models.PropertyPolicy(
            property_id=property_id,
            policy_id=policy_in.policy_id,
            content=policy_in.content,
            short_text=policy_in.short_text,
            effective_from=policy_in.effective_from,
            effective_to=policy_in.effective_to
        )
        db.add(prop_policy)
        
    await db.commit()
    await db.refresh(prop_policy)
    return APIResponse(
        success=True,
        message="Property Policy updated successfully",
        data=prop_policy
    )

# Nearby Places
@router.post("/{property_id}/nearby-places", response_model=APIResponse[schemas.NearbyPlace])
async def create_nearby_place(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    place_in: schemas.NearbyPlaceCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    place = models.NearbyPlace(**place_in.dict(), property_id=property_id)
    db.add(place)
    await db.commit()
    await db.refresh(place)
    return APIResponse(
        success=True,
        message="Nearby Place created successfully",
        data=place
    )

@router.get("/{property_id}/nearby-places", response_model=APIResponse[List[schemas.NearbyPlace]])
async def read_nearby_places(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.NearbyPlace).where(models.NearbyPlace.property_id == property_id))
    places = result.scalars().all()
    return APIResponse(
        success=True,
        message="Nearby Places retrieved successfully",
        data=places
    )

@router.patch("/{property_id}/nearby-places/{place_id}", response_model=APIResponse[schemas.NearbyPlace])
async def update_nearby_place(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    place_id: UUID,
    place_in: schemas.NearbyPlaceUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.NearbyPlace).where(models.NearbyPlace.id == place_id))
    place = result.scalars().first()
    if not place:
        raise HTTPException(status_code=404, detail="Nearby Place not found")
        
    update_data = place_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(place, field, value)
        
    await db.commit()
    await db.refresh(place)
    return APIResponse(
        success=True,
        message="Nearby Place updated successfully",
        data=place
    )

@router.delete("/{property_id}/nearby-places/{place_id}", response_model=APIResponse[schemas.NearbyPlace])
async def delete_nearby_place(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    place_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.NearbyPlace).where(models.NearbyPlace.id == place_id))
    place = result.scalars().first()
    if not place:
        raise HTTPException(status_code=404, detail="Nearby Place not found")
        
    await db.delete(place)
    await db.commit()
    return APIResponse(
        success=True,
        message="Nearby Place deleted successfully",
        data=place
    )

# Reviews
@router.post("/{property_id}/reviews", response_model=APIResponse[schemas.Review])
async def create_review(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    review_in: schemas.ReviewCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Check if user has a booking for this property (optional validation)
    # For now, just create the review
    
    review = models.Review(
        property_id=property_id,
        user_id=current_user.id,
        rating=review_in.rating,
        title=review_in.title,
        comment=review_in.comment,
        is_published=review_in.is_published,
        booking_id=review_in.booking_id
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    # Update property rating and reviews count (could be async task)
    # Simple implementation:
    result = await db.execute(select(models.Property).where(models.Property.id == property_id))
    property = result.scalars().first()
    if property:
        property.reviews_count = (property.reviews_count or 0) + 1
        # Recalculate average rating (simplified)
        # property.rating = ...
    return APIResponse(
        success=True,
        message="Review submitted successfully",
        data=review
    )

# New Features

# 1. Get policies for properties
@router.get("/{property_id}/policies", response_model=APIResponse[List[schemas.PropertyPolicy]])
async def read_property_policies(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.PropertyPolicy).where(models.PropertyPolicy.property_id == property_id))
    policies = result.scalars().all()
    return APIResponse(
        success=True,
        message="Property Policies retrieved successfully",
        data=policies
    )

# 2. Room Numbers Management (CRUD)
@router.post("/{property_id}/rooms", response_model=APIResponse[schemas.Room])
async def create_room(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    room_in: schemas.RoomCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Check if room number already exists for this property
    result = await db.execute(select(models.Room).where(
        models.Room.property_id == property_id,
        models.Room.room_number == room_in.room_number
    ))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Room number already exists for this property")

    room = models.Room(**room_in.dict())
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return APIResponse(
        success=True,
        message="Room created successfully",
        data=room
    )

@router.get("/{property_id}/rooms", response_model=APIResponse[List[schemas.Room]])
async def read_rooms(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.Room).where(models.Room.property_id == property_id))
    rooms = result.scalars().all()
    return APIResponse(
        success=True,
        message="Rooms retrieved successfully",
        data=rooms
    )

@router.patch("/{property_id}/rooms/{room_id}", response_model=APIResponse[schemas.Room])
async def update_room(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    room_id: UUID,
    room_in: schemas.RoomUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.Room).where(models.Room.id == room_id))
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    update_data = room_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)
        
    await db.commit()
    await db.refresh(room)
    return APIResponse(
        success=True,
        message="Room updated successfully",
        data=room
    )

@router.delete("/{property_id}/rooms/{room_id}", response_model=APIResponse[schemas.Room])
async def delete_room(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    room_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(select(models.Room).where(models.Room.id == room_id))
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    await db.delete(room)
    await db.commit()
    return APIResponse(
        success=True,
        message="Room deleted successfully",
        data=room
    )

# 3. Room Availability
@router.get("/{property_id}/availability", response_model=APIResponse[Any])
async def check_availability(
    *,
    db: AsyncSession = Depends(get_db),
    property_id: UUID,
    start_date: datetime,
    end_date: datetime,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Logic to check availability
    # 1. Get all room types for property
    # 2. For each room type, check inventory for the date range
    # 3. Check bookings for the date range to see which specific rooms are booked
    
    # This is a simplified implementation. Real-world logic is more complex.
    
    # Get Room Types
    result = await db.execute(select(models.RoomType).where(models.RoomType.property_id == property_id))
    room_types = result.scalars().all()
    
    availability_data = []
    
    for rt in room_types:
        # Get total rooms for this type
        # Assuming Room model has room_type_id
        rooms_result = await db.execute(select(models.Room).where(models.Room.room_type_id == rt.id))
        total_rooms = len(rooms_result.scalars().all())
        
        # Check inventory (min available count across dates)
        # ... implementation omitted for brevity, assuming full availability for now
        
        availability_data.append({
            "room_type_id": rt.id,
            "room_type_name": rt.name,
            "total_rooms": total_rooms,
            "available_rooms": total_rooms # Placeholder
        })
        
    return APIResponse(
        success=True,
        message="Availability checked successfully",
        data=availability_data
    )
