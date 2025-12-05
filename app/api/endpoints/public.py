from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import aliased, selectinload
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

# Moved from properties.py

@router.get("/properties/list", response_model=APIResponse[List[schemas.PropertyPublicDetail]])
async def read_public_properties_list(
    db: AsyncSession = Depends(get_db),
    destination_id: uuid.UUID = Query(..., description="Destination ID to filter properties"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    query = select(models.Property).where(
        models.Property.is_published == True, 
        models.Property.is_deleted == False,
        models.Property.destination_id == destination_id
    ).options(
        selectinload(models.Property.destination),
        selectinload(models.Property.rooms),
        selectinload(models.Property.property_amenities).selectinload(models.PropertyAmenity.amenity),
        selectinload(models.Property.property_policies).selectinload(models.PropertyPolicy.policy),
        selectinload(models.Property.nearby_places).selectinload(models.NearbyPlace.media),
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    properties = result.scalars().all()
    
    # Fetch Media for these properties
    property_ids = [p.id for p in properties]
    media_map = {}
    if property_ids:
        media_query = select(models.EntityMedia).where(
            models.EntityMedia.entity_type == 'property',
            models.EntityMedia.entity_id.in_(property_ids)
        ).options(selectinload(models.EntityMedia.media))
        media_result = await db.execute(media_query)
        all_media = media_result.scalars().all()
        
        for m in all_media:
            if m.entity_id not in media_map:
                media_map[m.entity_id] = []
            media_map[m.entity_id].append(m)

    public_properties = []
    for p in properties:
        # Transform to PropertyPublicDetail
        
        # Images
        p_media = media_map.get(p.id, [])
        # Sort by position
        p_media.sort(key=lambda x: x.position or 0)
        
        images = [m.media.url for m in p_media if m.media and m.media.url]
        property_image = next((m.media.url for m in p_media if m.is_primary and m.media and m.media.url), images[0] if images else None)
        
        # Amenities
        amenities_list = []
        for pa in p.property_amenities:
            if pa.enabled and pa.amenity:
                 # Try to get image from meta, or use a placeholder/logic
                 amenity_image = pa.amenity.meta.get('image') if pa.amenity.meta else None
                 # Try to get number from config
                 number = pa.config.get('number') if pa.config else None
                 
                 amenities_list.append(schemas.AmenityPublic(
                     id=pa.amenity.id,
                     image=amenity_image,
                     number=number,
                     label=pa.amenity.name
                 ))
        
        # Nearby Places
        nearby_list = []
        for np in p.nearby_places:
            nearby_list.append(schemas.NearbyPlacePublic(
                id=np.id,
                image=np.media.url if np.media else None,
                name=np.name,
                description=np.description
            ))
            
        # Rules (Policies)
        rules_list = []
        for pp in p.property_policies:
            if pp.policy:
                rules_list.append(schemas.RulePublic(
                    header=pp.policy.title,
                    description=pp.content or pp.policy.description
                ))
        
        public_properties.append(schemas.PropertyPublicDetail(
            id=p.id,
            title=p.name, # or p.short_title if available
            description=p.overview, # or p.short_title
            price=str(p.starting_price) if p.starting_price else None,
            rating=str(p.rating) if p.rating else None,
            reviews=str(p.reviews_count) if p.reviews_count else "0",
            days=p.recommended_days,
            nights=p.recommended_nights,
            guests=f"{p.min_guests}-{p.max_guests}" if p.min_guests and p.max_guests else None,
            location=f"{p.city}, {p.state}" if p.city and p.state else None,
            property_image=property_image,
            images=images,
            about=p.about,
            amenities=amenities_list,
            map_location=p.map_url,
            nearby_attractions=nearby_list,
            rules=rules_list,
            page_route=p.slug,
            suggestions=p.property_type # Placeholder
        ))

    return APIResponse(
        success=True,
        message="Properties retrieved successfully",
        data=public_properties,
        meta=Meta(limit=limit, offset=skip)
    )

@router.get("/properties", response_model=APIResponse[List[schemas.Property]])
async def read_properties(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    destination_id: Optional[uuid.UUID] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> Any:
    query = select(models.Property).where(models.Property.is_published == True, models.Property.is_deleted == False)
    
    if destination_id:
        query = query.where(models.Property.destination_id == destination_id)
    if min_price:
        query = query.where(models.Property.starting_price >= min_price)
    if max_price:
        query = query.where(models.Property.starting_price <= max_price)
    
    query = query.options(selectinload(models.Property.destination)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    properties = result.scalars().all()
    
    return APIResponse(
        success=True,
        message="Properties retrieved successfully",
        data=properties,
        meta=Meta(limit=limit, offset=skip)
    )

@router.get("/properties/{property_id}", response_model=APIResponse[schemas.Property])
async def read_property(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    query = select(models.Property).where(models.Property.id == property_id).options(
        selectinload(models.Property.destination),
        selectinload(models.Property.nearby_places),
    )
    result = await db.execute(query)
    property = result.scalars().first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return APIResponse(
        success=True,
        message="Property retrieved successfully",
        data=property
    )
