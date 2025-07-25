from pydantic import BaseModel, UUID4, Field

phone_regex = r'^\+?[1-9]\d{1,14}$'

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str = Field(..., pattern=phone_regex)

class CreateUserModel(UserBase):
    password: str

class UpdateUserModel(UserBase):
    ...
