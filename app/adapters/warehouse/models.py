import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pydantic import BaseModel as PydanticBaseModel
from pydantic import field_validator
from typing import Optional
from app.models.base import BaseModel


class Warehouse(BaseModel):
    __tablename__ = "warehouses"
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    assigned_agent_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    is_deleted = Column(Boolean, default=False)

    user_warehouse = relationship('UserWarehouse', back_populates='warehouse', cascade='all, delete-orphan')
    agents = relationship('UserModel', secondary='user_warehouse', back_populates='warehouses', overlaps="user_warehouse")
    
    amount_transactions = relationship("ProductAmountLedger", back_populates="warehouse")

    crop_warehouse = relationship('CropWarehouse', back_populates='warehouse', cascade='all, delete-orphan')
    crops = relationship('Crop', secondary='crop_warehouse', back_populates='warehouses', overlaps="crop_warehouse")
    
    amount_transactions = relationship("ProductAmountLedger", back_populates="warehouse", cascade="all, delete-orphan")
    goods_receiving = relationship(
        "GoodsReceiving", 
        back_populates="warehouse", 
        cascade="all, delete-orphan",
        foreign_keys="[GoodsReceiving.warehouse_id]"
    )



class UserWarehouse(BaseModel):
    __tablename__ = 'user_warehouse'
    
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    warehouse_id = Column(PG_UUID(as_uuid=True), ForeignKey('warehouses.id', ondelete='CASCADE'), primary_key=True)
    
    warehouse = relationship('Warehouse', back_populates='user_warehouse', overlaps="agents,warehouses")
    user = relationship('UserModel', back_populates='user_warehouse', overlaps="agents,warehouses")

class WarehouseDBSchema(PydanticBaseModel):
    id: Optional[uuid.UUID]
    description: Optional[str] = None
    location: str
    name: str
    
    model_config = {"from_attributes": True}

class WarehouseCreate(PydanticBaseModel):
    description: Optional[str] = None
    location: str
    name: str


class AgentWarehouseAssignment(PydanticBaseModel):
    warehouse_id: str
    agent_id: str