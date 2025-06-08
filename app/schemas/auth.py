from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
