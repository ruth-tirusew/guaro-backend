from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from pydantic import BaseModel as PydanticBaseModel
from typing import Optional

class Role(BaseModel):
    __tablename__ = 'roles'
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    user_roles = relationship('UserRole', back_populates='role', cascade='all, delete-orphan')
    role_resources = relationship('RoleResource', back_populates='role', cascade='all, delete-orphan')
    users = relationship('User', secondary='user_roles', back_populates='roles')


class UserRole(BaseModel):
    __tablename__ = 'user_roles'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    role = relationship('Role', back_populates='user_roles')
    user = relationship('User', back_populates='user_roles')


class RoleDBSchema(PydanticBaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    
    model_config = {"from_attributes": True}

class RoleCreate(PydanticBaseModel):
    name: str
    description: Optional[str] = None