from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    analyst = "analyst"
    executive = "executive"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: RoleEnum = RoleEnum.analyst

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class UserResponse(UserBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
