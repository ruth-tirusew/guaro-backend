import uuid
from pydantic import BaseModel, model_validator, field_validator
from typing import Optional, List


class RoleBase(BaseModel):
    name: str
    description: str

class RoleRead(RoleBase):
    id: uuid.UUID
    model_config = {"from_attributes": True}

class RoleList(BaseModel):
    roles: List[RoleRead]

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None