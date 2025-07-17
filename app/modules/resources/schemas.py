from pydantic import BaseModel
from typing import Optional, List

class ResourceBase(BaseModel):
    action: Optional[str] = None
    name: str
    resource: str
class ResourceRead(ResourceBase):
    id: str
    model_config = {"from_attributes": True}
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

    # Pydantic v2: use model_validator
    from pydantic import model_validator
    _validate = model_validator(mode="after")(validate_at_least_one_field)
