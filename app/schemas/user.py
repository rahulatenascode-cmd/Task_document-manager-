from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserResponse(UserBase):
    id: int
    role: str

    model_config = {
        "from_attributes": True
    }


class UserAdminResponse(UserBase):
    id: int
    role: str

    model_config = {
        "from_attributes": True
    }