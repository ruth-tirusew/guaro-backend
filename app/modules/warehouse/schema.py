import datetime
from pydantic import BaseModel as PydanticBaseModel
from pydantic import field_validator, EmailStr, Field, constr
from typing import Optional,List
import uuid



class Warehouse(PydanticBaseModel):
    id: Optional[uuid.UUID]
    description: Optional[str] = None
    location: str
    name: str

    model_config = {"from_attributes": True}

class WarehouseCreate(PydanticBaseModel):
    description: Optional[str] = None
    location: str
    name: str

class WarehouseList(PydanticBaseModel):
    warehouses: List[Warehouse]

class AgentWarehouseAssignment(PydanticBaseModel):
    warehouse_id: str
    agent_id: str

class AssignedAgent(PydanticBaseModel):
    id: uuid.UUID
    first_name: constr(strip_whitespace=True)
    last_name: constr(strip_whitespace=True)
    email: EmailStr
    phone: str = Field(pattern=r"^\+?\d{7,15}$")
    created_at: datetime
    updated_at: datetime

    model_config = {"arbitrary_types_allowed":True, "from_attributes": True}


class AgentsList(PydanticBaseModel):
    agents: List[AssignedAgent]
