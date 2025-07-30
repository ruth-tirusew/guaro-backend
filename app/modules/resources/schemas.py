import uuid
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List

class ResourceBase(BaseModel):
    action: Optional[str] = None
    name: str
    resource: str
class ResourceRead(ResourceBase):
    id: uuid.UUID
    model_config = {"from_attributes": True}

class ResourceList(BaseModel):
    resources: List[ResourceRead]

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    action: Optional[str] = None
    name: Optional[str] = None
    resource: Optional[str] = None
