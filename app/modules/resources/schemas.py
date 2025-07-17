import uuid
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List

class ResourceBase(BaseModel):
    action: Optional[str] = None
    name: str
    resource: str
class ResourceRead(ResourceBase):
    id: str
    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v):
        print(v)
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

class ResourceList(BaseModel):
    resources: List[ResourceRead]

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    action: Optional[str] = None
    name: Optional[str] = None
    resource: Optional[str] = None

    @classmethod
    def validate_at_least_one_field(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values

    _validate = model_validator(mode="after")(validate_at_least_one_field)
