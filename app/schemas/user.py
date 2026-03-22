import uuid
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")


class UserAuthBase(UserBase):
    password: str = Field(..., min_length=12, description="Password for the user account")


class UserLogin(UserAuthBase):
    pass


class UserRegister(UserAuthBase):
    pass


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)


class UserResponse(UserBase):
    id: uuid.UUID = Field(..., description="UUID of the user")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
