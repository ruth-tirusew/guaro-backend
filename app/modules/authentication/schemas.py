from pydantic import BaseModel, UUID4, Field

phone_regex = r'^\+?[1-9]\d{1,14}$'

class CreateUserModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str = Field(..., pattern=phone_regex)
    password: str