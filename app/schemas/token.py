from typing import Optional, List
from pydantic import BaseModel

class RoleScope(BaseModel):
    role: str
    scope: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    roles: List[RoleScope] = []
    default_tenant: Optional[str] = None
    type: str = "access"
    iat: Optional[int] = None
    exp: Optional[int] = None

class Login(BaseModel):
    username: str
    password: str
