from typing import Optional, List, Any
from pydantic import BaseModel
from app.schemas.token import RoleScope

class UserSchema(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    roles: List[RoleScope] = []
    default_tenant: Optional[str] = None

class LoginResponseData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    expires_in: int
    user: UserSchema

class LoginResponse(BaseModel):
    meta: dict
    data: LoginResponseData
    error: Optional[str] = None
