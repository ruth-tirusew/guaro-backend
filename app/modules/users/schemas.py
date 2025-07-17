import re
import uuid
from pydantic import BaseModel, EmailStr, field_validator, model_validator, ValidationInfo
from typing import List, Optional

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")

class UserBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: Optional[EmailStr] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Name must not be empty")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def phone_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError("Phone must not be empty")
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone number format")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v):
        if v is not None and not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [self.first_name, self.last_name, self.phone, self.email]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self

class UserRead(UserBase):
    id: str
    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v):
        print(v)
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
        



class UserList(BaseModel):
    users: List[UserRead]    
