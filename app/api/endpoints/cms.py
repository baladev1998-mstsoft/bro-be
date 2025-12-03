from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.api import deps
from app.models.cms import CMSPage, CMSPageTranslation, CMSSection, CMSSectionContent, CMSPageVersion
from app.schemas import cms as schemas

router = APIRouter()

def filter_page_content(page: CMSPage, lang: str):
    """
    Recursively filter page content by language.
    """
    # Filter translations
    page.translations = [t for t in page.translations if t.language_code == lang]
    
    # Filter section contents
    for section in page.sections:
        section.contents = [c for c in section.contents if c.language_code == lang]
        
    # Recursively filter children
    for child in page.children:
        filter_page_content(child, lang)
    
    return page

@router.get("/pages", response_model=List[schemas.CMSPage])
async def read_pages(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[UUID] = None,
    lang: str = Query("en", min_length=2, max_length=2),
    draft: bool = False
) -> Any:
    """
    Retrieve pages. By default, returns published versions. Set draft=true to get current drafts.
    """
    if draft:
        # Fetch from relational tables (Draft)
        query = select(CMSPage).options(
            selectinload(CMSPage.translations),
            selectinload(CMSPage.sections).selectinload(CMSSection.contents),
            selectinload(CMSPage.children).selectinload(CMSPage.translations),
            selectinload(CMSPage.children).selectinload(CMSPage.sections).selectinload(CMSSection.contents),
            selectinload(CMSPage.children).selectinload(CMSPage.children)
        )
        if parent_id:
            query = query.filter(CMSPage.parent_id == parent_id)
        
        result = await db.execute(query.offset(skip).limit(limit))
        pages = result.scalars().all()
        
        # Apply language filter
        filtered_pages = [filter_page_content(p, lang) for p in pages]
        return filtered_pages
    else:
        # Fetch from published versions
        # We need to find the latest published version for each page
        # This is complex with SQL directly if we want list + pagination + parent_id filter on the JSON data
        # For simplicity, we can fetch published versions joined with CMSPage to filter by parent_id
        
        query = select(CMSPageVersion).join(CMSPage).filter(CMSPageVersion.is_published == True)
        
        if parent_id:
            query = query.filter(CMSPage.parent_id == parent_id)
            
        result = await db.execute(query.offset(skip).limit(limit))
        versions = result.scalars().all()
        
        # Convert JSON data back to CMSPage schema structure
        # And apply language filter on the JSON data
        pages = []
        for v in versions:
            page_data = v.data
            # We need to reconstruct the object or just return the dict if schema allows
            # But schema expects CMSPage object.
            # Let's try to map it back or use a flexible return type.
            # Actually, since we return List[schemas.CMSPage], we should return objects matching that.
            # The JSON data in v.data matches the schema structure.
            
            # Filter JSON data by language
            # Helper to filter dict
            def filter_json_content(data, lang):
                if "translations" in data:
                    data["translations"] = [t for t in data["translations"] if t["language_code"] == lang]
                if "sections" in data:
                    for s in data["sections"]:
                        if "contents" in s:
                            s["contents"] = [c for c in s["contents"] if c["language_code"] == lang]
                if "children" in data:
                    for c in data["children"]:
                        filter_json_content(c, lang)
                return data

            filtered_data = filter_json_content(page_data, lang)
            pages.append(filtered_data)
            
        return pages

@router.post("/pages", response_model=schemas.CMSPage)
async def create_page(
    *,
    db: AsyncSession = Depends(deps.get_db),
    page_in: schemas.CMSPageCreate,
) -> Any:
    """
    Create new page.
    """
    if page_in.parent_id:
        result = await db.execute(select(CMSPage).filter(CMSPage.id == page_in.parent_id))
        parent = result.scalars().first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent page not found")

    page = CMSPage(
        slug=page_in.slug,
        is_published=page_in.is_published,
        parent_id=page_in.parent_id
    )
    db.add(page)
    await db.commit()
    
    # Fetch with relationships for Pydantic serialization
    query = select(CMSPage).options(
        selectinload(CMSPage.translations),
        selectinload(CMSPage.sections).selectinload(CMSSection.contents),
        selectinload(CMSPage.children).selectinload(CMSPage.translations),
        selectinload(CMSPage.children).selectinload(CMSPage.sections).selectinload(CMSSection.contents),
        selectinload(CMSPage.children).selectinload(CMSPage.children)
    ).filter(CMSPage.id == page.id)
    result = await db.execute(query)
    page = result.scalars().first()
    return page

@router.get("/pages/{slug}", response_model=schemas.CMSPage)
async def read_page(
    *,
    db: AsyncSession = Depends(deps.get_db),
    slug: str,
    lang: str = Query("en", min_length=2, max_length=2),
    draft: bool = False
) -> Any:
    """
    Get page by slug. By default, returns published version. Set draft=true to get current draft.
    """
    if draft:
        query = select(CMSPage).options(
            selectinload(CMSPage.translations),
            selectinload(CMSPage.sections).selectinload(CMSSection.contents),
            selectinload(CMSPage.children).selectinload(CMSPage.translations),
            selectinload(CMSPage.children).selectinload(CMSPage.sections).selectinload(CMSSection.contents),
            selectinload(CMSPage.children).selectinload(CMSPage.children)
        ).filter(CMSPage.slug == slug)
        
        result = await db.execute(query)
        page = result.scalars().first()
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        
        # Apply language filter
        filter_page_content(page, lang)
        return page
    else:
        # Fetch published version
        query = select(CMSPageVersion).join(CMSPage).filter(
            CMSPage.slug == slug,
            CMSPageVersion.is_published == True
        )
        result = await db.execute(query)
        version = result.scalars().first()
        
        if not version:
            # Fallback: If no published version exists, user asked "provide previous version... until true".
            # If NEVER published, we should probably return 404 or empty?
            # Or maybe the user implies if it's NOT published, we shouldn't see it at all?
            # "if a page is is_published = false ... the whole page content will not provided"
            raise HTTPException(status_code=404, detail="Page not found or not published")
            
        page_data = version.data
        
        # Filter JSON data by language
        def filter_json_content(data, lang):
            if "translations" in data:
                data["translations"] = [t for t in data["translations"] if t["language_code"] == lang]
            if "sections" in data:
                for s in data["sections"]:
                    if "contents" in s:
                        s["contents"] = [c for c in s["contents"] if c["language_code"] == lang]
            if "children" in data:
                for c in data["children"]:
                    filter_json_content(c, lang)
            return data

        filtered_data = filter_json_content(page_data, lang)
        return filtered_data

@router.put("/pages/{page_id}", response_model=schemas.CMSPage)
async def update_page(
    *,
    db: AsyncSession = Depends(deps.get_db),
    page_id: UUID,
    page_in: schemas.CMSPageUpdate,
) -> Any:
    """
    Update a page.
    """
    result = await db.execute(select(CMSPage).filter(CMSPage.id == page_id))
    page = result.scalars().first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    update_data = page_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(page, field, value)
    
    db.add(page)
    await db.commit()
    
    # Fetch with relationships
    query = select(CMSPage).options(
        selectinload(CMSPage.translations),
        selectinload(CMSPage.sections).selectinload(CMSSection.contents),
        selectinload(CMSPage.children).selectinload(CMSPage.translations),
        selectinload(CMSPage.children).selectinload(CMSPage.sections).selectinload(CMSSection.contents),
        selectinload(CMSPage.children).selectinload(CMSPage.children)
    ).filter(CMSPage.id == page.id)
    result = await db.execute(query)
    page = result.scalars().first()
    return page

@router.post("/pages/{page_id}/translations", response_model=schemas.CMSPageTranslation)
async def create_page_translation(
    *,
    db: AsyncSession = Depends(deps.get_db),
    page_id: UUID,
    translation_in: schemas.CMSPageTranslationCreate,
) -> Any:
    """
    Add translation to a page.
    """
    result = await db.execute(select(CMSPage).filter(CMSPage.id == page_id))
    page = result.scalars().first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
        
    translation = CMSPageTranslation(
        page_id=page_id,
        language_code=translation_in.language_code,
        title=translation_in.title,
        seo_metadata=translation_in.seo_metadata
    )
    db.add(translation)
    await db.commit()
    await db.refresh(translation)
    return translation

@router.post("/pages/{page_id}/sections", response_model=schemas.CMSSection)
async def create_section(
    *,
    db: AsyncSession = Depends(deps.get_db),
    page_id: UUID,
    section_in: schemas.CMSSectionCreate,
) -> Any:
    """
    Add section to a page.
    """
    result = await db.execute(select(CMSPage).filter(CMSPage.id == page_id))
    page = result.scalars().first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
        
    section = CMSSection(
        page_id=page_id,
        section_key=section_in.section_key,
        type=section_in.type,
        order_index=section_in.order_index,
        is_active=section_in.is_active
    )
    db.add(section)
    await db.commit()
    
    # Fetch with relationships
    query = select(CMSSection).options(
        selectinload(CMSSection.contents)
    ).filter(CMSSection.id == section.id)
    result = await db.execute(query)
    section = result.scalars().first()
    return section

@router.post("/sections/{section_id}/content", response_model=schemas.CMSSectionContent)
async def create_section_content(
    *,
    db: AsyncSession = Depends(deps.get_db),
    section_id: UUID,
    content_in: schemas.CMSSectionContentCreate,
) -> Any:
    """
    Add content to a section.
    """
    result = await db.execute(select(CMSSection).filter(CMSSection.id == section_id))
    section = result.scalars().first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    content = CMSSectionContent(
        section_id=section_id,
        language_code=content_in.language_code,
        content=content_in.content
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return content

@router.put("/pages/{page_id}/translations", response_model=schemas.CMSPageTranslation)
async def update_page_translation(
    *,
    db: AsyncSession = Depends(deps.get_db),
    page_id: UUID,
    translation_in: schemas.CMSPageTranslationUpdate,
) -> Any:
    """
    Update translation for a page.
    """
    result = await db.execute(select(CMSPageTranslation).filter(
        CMSPageTranslation.page_id == page_id,
        CMSPageTranslation.language_code == translation_in.language_code
    ))
    translation = result.scalars().first()
    
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
        
    update_data = translation_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(translation, field, value)
        
    db.add(translation)
    await db.commit()
    await db.refresh(translation)
    return translation

@router.put("/pages/{page_id}/sections", response_model=schemas.CMSSection)
async def update_section_by_page(
    *,
    db: AsyncSession = Depends(deps.get_db),
    page_id: UUID,
    section_in: schemas.CMSSectionUpdate,
) -> Any:
    """
    Update a section by page_id and section_key (if provided) or just update section details if section_id was known.
    Since the user asked for PUT /pages/{page_id}/sections, and sections are identified by key per page,
    we can try to find the section by key.
    """
    if not section_in.section_key:
         raise HTTPException(status_code=400, detail="section_key required to identify section")

    result = await db.execute(select(CMSSection).filter(
        CMSSection.page_id == page_id,
        CMSSection.section_key == section_in.section_key
    ))
    section = result.scalars().first()
    
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    update_data = section_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(section, field, value)
        
    db.add(section)
    await db.commit()
    
    # Fetch with relationships
    query = select(CMSSection).options(
        selectinload(CMSSection.contents)
    ).filter(CMSSection.id == section.id)
    result = await db.execute(query)
    section = result.scalars().first()
    return section

@router.put("/sections/{section_id}/content", response_model=schemas.CMSSectionContent)
async def update_section_content(
    *,
    db: AsyncSession = Depends(deps.get_db),
    section_id: UUID,
    content_in: schemas.CMSSectionContentUpdate,
) -> Any:
    """
    Update content for a section.
    """
    result = await db.execute(select(CMSSectionContent).filter(
        CMSSectionContent.section_id == section_id,
        CMSSectionContent.language_code == content_in.language_code
    ))
    content = result.scalars().first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
        
    update_data = content_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
        
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return content

@router.post("/pages/{page_id}/publish", response_model=schemas.CMSPageVersion)
async def publish_page(
    *,
    db: AsyncSession = Depends(deps.get_db),
    page_id: UUID,
) -> Any:
    """
    Publish a page: Snapshot current state to a new version.
    """
    # Fetch full page data
    query = select(CMSPage).options(
        selectinload(CMSPage.translations),
        selectinload(CMSPage.sections).selectinload(CMSSection.contents),
        selectinload(CMSPage.children).selectinload(CMSPage.translations),
        selectinload(CMSPage.children).selectinload(CMSPage.sections).selectinload(CMSSection.contents),
        selectinload(CMSPage.children).selectinload(CMSPage.children)
    ).filter(CMSPage.id == page_id)
    result = await db.execute(query)
    page = result.scalars().first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # Serialize page data
    from fastapi.encoders import jsonable_encoder
    page_data = jsonable_encoder(schemas.CMSPage.from_orm(page))

    # Get next version number
    result = await db.execute(select(CMSPageVersion).filter(CMSPageVersion.page_id == page_id).order_by(CMSPageVersion.version.desc()))
    last_version = result.scalars().first()
    new_version_num = (last_version.version + 1) if last_version else 1
    
    # Unpublish previous versions
    result = await db.execute(select(CMSPageVersion).filter(CMSPageVersion.page_id == page_id, CMSPageVersion.is_published == True))
    old_published = result.scalars().all()
    for v in old_published:
        v.is_published = False
        db.add(v)
    
    # Create new version
    version = CMSPageVersion(
        page_id=page_id,
        version=new_version_num,
        data=page_data,
        is_published=True
    )
    db.add(version)
    
    # Also update the main page is_published to True
    page.is_published = True
    db.add(page)
    
    await db.commit()
    await db.refresh(version)
    return version

@router.get("/public/pages/{slug}", response_model=schemas.CMSPage)
async def read_public_page(
    *,
    db: AsyncSession = Depends(deps.get_db),
    slug: str,
    lang: str = Query("en", min_length=2, max_length=2)
) -> Any:
    """
    Get public page by slug. Always returns published version.
    """
    return await read_page(db=db, slug=slug, lang=lang, draft=False)
