from app.models.base import BaseModel
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

import uuid



class Resource(BaseModel):
    __tablename__ = 'resources'
    action = Column(String(255))
    name = Column(String(255))
    resource = Column(String(255))
    role_resources = relationship('RoleResource', back_populates='resource', cascade='all, delete-orphan')



class RoleResource(BaseModel):
    __tablename__ = 'role_resources'
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey('resources.id', ondelete='CASCADE'), primary_key=True)
    role = relationship('Role', back_populates='role_resources')
    resource = relationship('Resource', back_populates='role_resources')
