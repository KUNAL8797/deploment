from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    ADMIN = 'admin'
    CONTRIBUTOR = 'contributor'

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str
