from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

T = TypeVar("T")

class Meta(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None
    method: Optional[str] = None
    requestId: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    total: Optional[int] = None

class ErrorDetails(BaseModel):
    code: Optional[str] = None
    details: Optional[Any] = None

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[ErrorDetails] = None
    meta: Optional[Meta] = None
