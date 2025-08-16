from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    select,
    func,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from enum import Enum as PyEnum
from app.models.base import BaseModel


class OrderStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class Customer(BaseModel):
    __tablename__ = 'customers'
    
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True, unique=True)
    email = Column(String(255), nullable=True, unique=True)

    
    orders = relationship('Orders', back_populates='customer', cascade='all, delete-orphan')
    
    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @full_name.expression
    def full_name(cls):
        return func.concat(cls.first_name, ' ', cls.last_name)


class Orders(BaseModel):
    __tablename__ = 'orders'
    
    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    warehouse_id = Column(PG_UUID(as_uuid=True), ForeignKey('warehouses.id', ondelete='CASCADE'), nullable=False)
    
    order_number = Column(String(100), nullable=False, unique=True, index=True)
    order_date = Column(DateTime, default=datetime.now(timezone.utc))
    delivery_date = Column(DateTime, nullable=True)
    
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    
    subtotal = Column(Numeric(12, 4), default=0.0)
    discount = Column(Numeric(12, 4), default=0.0)
    adjustment = Column(Numeric(12, 4), default=0.0)
    tax_amount = Column(Numeric(12, 4), default=0.0)
    total_amount = Column(Numeric(12, 4), default=0.0)
    
    notes = Column(Text, nullable=True)
    
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    modified_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    customer = relationship('Customer', back_populates='orders')
    warehouse = relationship('Warehouse', back_populates='orders')
    order_items = relationship('OrderItems', back_populates='order', cascade='all, delete-orphan')
    
    creator = relationship("UserModel", foreign_keys=[created_by])
    modifier = relationship("UserModel", foreign_keys=[modified_by])
    
    @hybrid_property
    def calculated_total(self):
        """Calculate total from subtotal, discount, adjustment, and tax"""
        return (self.subtotal or 0) - (self.discount or 0) + (self.adjustment or 0) + (self.tax_amount or 0)
    
    @calculated_total.expression
    def calculated_total(cls):
        return (
            func.coalesce(cls.subtotal, 0) - 
            func.coalesce(cls.discount, 0) + 
            func.coalesce(cls.adjustment, 0) + 
            func.coalesce(cls.tax_amount, 0)
        )
    
    @hybrid_property
    def items_count(self):
        """Count of order items"""
        return len(self.order_items)
    
    @items_count.expression
    def items_count(cls):
        return (
            select(func.count(OrderItems.id))
            .where(OrderItems.order_id == cls.id)
            .scalar_subquery()
        )


class OrderItems(BaseModel):
    __tablename__ = 'order_items'
    
    order_id = Column(PG_UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    batch_id = Column(PG_UUID(as_uuid=True), ForeignKey('product_batches.id', ondelete='SET NULL'), nullable=True)
    
    quantity = Column(Numeric(12, 4), nullable=False)
    unit_price = Column(Numeric(12, 4), nullable=False)
    discount_amount = Column(Numeric(12, 4), default=0.0)
    tax_amount = Column(Numeric(12, 4), default=0.0)
    
    # Store product details at time of order
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=True)
    unit_of_measure = Column(String(50), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    order = relationship('Orders', back_populates='order_items')
    product = relationship('Product', backref='order_items')
    batch = relationship('ProductBatch', backref='order_items')
    
    @hybrid_property
    def line_total(self):
        """Calculate line total: (quantity * unit_price) - discount + tax"""
        return (self.quantity * self.unit_price) - (self.discount_amount or 0) + (self.tax_amount or 0)
    
    @line_total.expression
    def line_total(cls):
        return (
            (cls.quantity * cls.unit_price) - 
            func.coalesce(cls.discount_amount, 0) + 
            func.coalesce(cls.tax_amount, 0)
        )
    
    @hybrid_property
    def subtotal(self):
        """Calculate subtotal before discount and tax"""
        return self.quantity * self.unit_price
    
    @subtotal.expression
    def subtotal(cls):
        return cls.quantity * cls.unit_price