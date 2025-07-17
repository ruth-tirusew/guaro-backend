from app.models.base import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel as PydanticBaseModel
from typing import Optional

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
