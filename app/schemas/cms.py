from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# Shared properties
class CMSPageBase(BaseModel):
    slug: str
    is_published: bool = False
    parent_id: Optional[UUID] = None

class CMSPageCreate(CMSPageBase):
    pass

class CMSPageUpdate(CMSPageBase):
    slug: Optional[str] = None
    is_published: Optional[bool] = None

class CMSPageTranslationBase(BaseModel):
    language_code: str
    title: str
    seo_metadata: Optional[Dict[str, Any]] = None

class CMSPageTranslationCreate(CMSPageTranslationBase):
    pass

class CMSPageTranslationUpdate(CMSPageTranslationBase):
    pass

class CMSPageTranslationInDBBase(CMSPageTranslationBase):
    id: UUID
    page_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CMSPageTranslation(CMSPageTranslationInDBBase):
    pass

class CMSSectionBase(BaseModel):
    section_key: str
    type: str
    order_index: int = 0
    is_active: bool = True

class CMSSectionCreate(CMSSectionBase):
    pass

class CMSSectionUpdate(CMSSectionBase):
    section_key: Optional[str] = None
    type: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None

class CMSSectionContentBase(BaseModel):
    language_code: str
    content: Dict[str, Any]

class CMSSectionContentCreate(CMSSectionContentBase):
    pass

class CMSSectionContentUpdate(CMSSectionContentBase):
    pass

class CMSSectionContentInDBBase(CMSSectionContentBase):
    id: UUID
    section_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CMSSectionContent(CMSSectionContentInDBBase):
    pass

class CMSSectionInDBBase(CMSSectionBase):
    id: UUID
    page_id: UUID
    created_at: datetime
    updated_at: datetime
    contents: List[CMSSectionContent] = []

    class Config:
        from_attributes = True

class CMSSection(CMSSectionInDBBase):
    pass

class CMSPageVersionBase(BaseModel):
    version: int
    data: Dict[str, Any]
    is_published: bool
    created_at: datetime

class CMSPageVersion(CMSPageVersionBase):
    id: UUID
    page_id: UUID

    class Config:
        from_attributes = True

class CMSPageInDBBase(CMSPageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    translations: List[CMSPageTranslation] = []
    sections: List[CMSSection] = []
    children: List['CMSPage'] = []

    class Config:
        from_attributes = True

class CMSPage(CMSPageInDBBase):
    pass

CMSPage.model_rebuild()
