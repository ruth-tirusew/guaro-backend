from app.models.base import BaseModel
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship


class UserModel(BaseModel):
    __tablename__='users'

    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone =  Column(String(20), nullable=False, unique=True)
    email = Column(String(255))

    user_roles = relationship('UserRole', back_populates='user', cascade='all, delete-orphan')
    roles = relationship('Role', secondary='user_roles', back_populates='users')
    
