import uuid
from pydantic import BaseModel, model_validator, field_validator
from typing import Optional, List


class RoleBase(BaseModel):
    name: str
    description: str

class RoleRead(RoleBase):
    id: str
    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

class RoleList(BaseModel):
    roles: List[RoleRead]

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def validate_at_least_one_field(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values

    _validate = model_validator(mode="after")(validate_at_least_one_field)
