from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: str

    class Config:
        orm_mode = True

class UserList(BaseModel):
    users: List[UserRead]
    