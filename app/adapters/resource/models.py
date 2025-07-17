import uuid

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from pydantic import BaseModel as PydanticBaseModel
from pydantic import field_validator
from typing import Optional

class Resource(BaseModel):
    __tablename__ = 'resources'
    action = Column(String(255))
    name = Column(String(255))
    resource = Column(String(255))
    role_resources = relationship('RoleResource', back_populates='resource', cascade='all, delete-orphan')


class ResourceDBSchema(PydanticBaseModel):
    id: Optional[str]
    action: Optional[str] = None
    name: str
    resource: str
    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    

class ResourceCreate(PydanticBaseModel):
    action: Optional[str] = None
    name: str
    resource: str
