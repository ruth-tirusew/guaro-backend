import uuid

from pydantic import BaseModel as PydanticBaseModel
from pydantic import field_validator
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import Optional

from app.models.base import BaseModel

class Role(BaseModel):
    __tablename__ = 'roles'
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    user_roles = relationship('UserRole', back_populates='role', cascade='all, delete-orphan')
    role_resources = relationship('RoleResource', back_populates='role', cascade='all, delete-orphan')
    users = relationship('UserModel', secondary='user_roles', back_populates='roles', overlaps="user_roles")


class UserRole(BaseModel):
    __tablename__ = 'user_roles'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    role = relationship('Role', back_populates='user_roles',overlaps="roles,users")
    user = relationship('UserModel', back_populates='user_roles', overlaps="roles,users")


class RoleResource(BaseModel):
    __tablename__ = 'role_resources'
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey('resources.id', ondelete='CASCADE'), primary_key=True)
    role = relationship('Role', back_populates='role_resources')
    resource = relationship('Resource', back_populates='role_resources')


class RoleDBSchema(PydanticBaseModel):
    id: Optional[uuid.UUID]
    name: str
    description: Optional[str] = None
    
    model_config = {"from_attributes": True}

class RoleCreate(PydanticBaseModel):
    name: str
    description: Optional[str] = None