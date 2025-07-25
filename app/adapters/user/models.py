from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from typing import Optional

from app.models.base import BaseModel

class UserDBSchema(PydanticBaseModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None

    model_config = {"from_attributes": True}

class UserModel(BaseModel):
    __tablename__ = 'users'

    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    email = Column(String(255), unique=True)

    user_roles = relationship('UserRole', back_populates='user', cascade='all, delete-orphan')
    roles = relationship('Role', secondary='user_roles', back_populates='users')
    
    user_warehouse = relationship('UserWarehouse', back_populates='user', cascade='all, delete-orphan')
    warehouses = relationship('Warehouse', secondary='user_warehouse', back_populates='agents')

class UserProvider(BaseModel):
    __tablename__ = 'user_providers'

    provider_id = Column(String(255), nullable=False, primary_key=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)

