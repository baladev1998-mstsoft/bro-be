from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.core.config import settings
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime, timezone

from app.schemas.response import APIResponse

router = APIRouter()

# Initialize S3 client (sync for now, or use aiobotocore if available, but standard boto3 is common)
# For async, we might want to run this in a threadpool or use aiobotocore.
# For simplicity in this scaffold, we'll use boto3 directly.

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

@router.post("/presign", response_model=APIResponse[schemas.MediaPresignResponse])
async def presign_upload(
    *,
    media_in: schemas.MediaPresign,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Generate S3 key
    file_ext = media_in.file_name.split('.')[-1] if '.' in media_in.file_name else 'bin'
    s3_key = f"uploads/{current_user.id}/{uuid.uuid4()}.{file_ext}"
    
    s3_client = get_s3_client()
    try:
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': s3_key,
                'ContentType': media_in.content_type
            },
            ExpiresIn=3600
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return APIResponse(
        success=True,
        message="Presigned URL generated successfully",
        data=schemas.MediaPresignResponse(
            upload_url=upload_url,
            s3_key=s3_key
        )
    )

@router.post("/complete", response_model=APIResponse[schemas.Media])
async def complete_upload(
    *,
    db: AsyncSession = Depends(get_db),
    media_in: schemas.MediaComplete,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Create Media record
    media = models.Media(
        provider="s3",
        s3_bucket=settings.S3_BUCKET_NAME,
        s3_key=media_in.s3_key,
        file_name=media_in.file_name,
        content_type=media_in.content_type,
        size_bytes=media_in.size_bytes,
        width=media_in.width,
        height=media_in.height,
        uploaded_by=current_user.id,
        url=f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{media_in.s3_key}" # Simple URL construction
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return APIResponse(
        success=True,
        message="Media upload completed successfully",
        data=media
    )

@router.post("/entity_media", response_model=APIResponse[schemas.EntityMedia])
async def attach_entity_media(
    *,
    db: AsyncSession = Depends(get_db),
    entity_media_in: schemas.EntityMediaCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Check if media exists
    result = await db.execute(select(models.Media).where(models.Media.id == entity_media_in.media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
        
    # Create EntityMedia
    entity_media = models.EntityMedia(
        media_id=entity_media_in.media_id,
        entity_type=entity_media_in.entity_type,
        entity_id=entity_media_in.entity_id,
        role=entity_media_in.role,
        alt_text=entity_media_in.alt_text,
        caption=entity_media_in.caption,
        position=entity_media_in.position,
        is_primary=entity_media_in.is_primary
    )
    db.add(entity_media)
    await db.commit()
    await db.refresh(entity_media)
    return APIResponse(
        success=True,
        message="Entity media attached successfully",
        data=entity_media
    )
