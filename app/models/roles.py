from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Role(BaseModel):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    user_roles = relationship('UserRole', back_populates='role', cascade='all, delete-orphan')
    role_resources = relationship('RoleResource', back_populates='role', cascade='all, delete-orphan')
    users = relationship('UserModel', secondary='user_roles', back_populates='roles')

class Resource(BaseModel):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(255))
    name = Column(String(255))
    resource = Column(String(255))
    role_resources = relationship('RoleResource', back_populates='resource', cascade='all, delete-orphan')

class UserRole(BaseModel):
    __tablename__ = 'user_roles'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    role = relationship('Role', back_populates='user_roles')
    user = relationship('UserModel', back_populates='user_roles')

class RoleResource(BaseModel):
    __tablename__ = 'role_resources'
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    resource_id = Column(Integer, ForeignKey('resources.id', ondelete='CASCADE'), primary_key=True)
    role = relationship('Role', back_populates='role_resources')
    resource = relationship('Resource', back_populates='role_resources')

# Pydantic schemas for roles
from pydantic import BaseModel
from typing import Optional

class RoleSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    class Config:
        orm_mode = True

class RoleResourceSchema(BaseModel):
    role_id: int
    resource_id: int
    class Config:
        orm_mode = True 