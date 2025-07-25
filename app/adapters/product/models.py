from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"
    
    image = Column(String(100))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), default=0.0)
    unit = Column(String(100))
    available_amount = Column(Numeric(10, 2), default=0.0)
    raw_material_id = Column(PG_UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    
    # Relationships
    raw_material = relationship("Crop", back_populates="products")
    price_ledger = relationship("ProductPriceLedger", back_populates="product", cascade="all, delete-orphan")
    goods_receiving = relationship("ProductAmountLedger", back_populates="product", cascade="all, delete-orphan")
    
    product_warehouse = relationship('ProductWarehouse', back_populates='product', cascade='all, delete-orphan')
    warehouses = relationship('Warehouse', secondary='product_warehouse', back_populates='products')


class ProductPriceLedger(BaseModel):
    __tablename__ = "product_price_ledger"
    
    previous_price = Column(Numeric(10, 2), default=0.0)
    updated_price = Column(Numeric(10, 2), default=0.0)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    product = relationship("Product", back_populates="price_ledger")


class ProductAmountLedger(BaseModel):
    __tablename__ = "product_amount_ledger"
    
    previous_amount = Column(Numeric(10, 2), default=0.0)
    updated_amount = Column(Numeric(10, 2), default=0.0)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)

    product = relationship("Product", back_populates="goods_receiving")


class ProductWarehouse(BaseModel):
    __tablename__ = 'product_warehouse'
    
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    warehouse_id = Column(PG_UUID(as_uuid=True), ForeignKey('warehouses.id', ondelete='CASCADE'), primary_key=True)

    warehouse = relationship('Warehouse', back_populates='product_warehouse')
    product = relationship('Product', back_populates='product_warehouse')
