from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, Boolean, Enum, select, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import BaseModel


class TransactionType(PyEnum):
    PURCHASE = "purchase"
    SALE = "sale"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"
    EXPIRY = "expiry"


class Category(BaseModel):
    __tablename__ = "categories"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Relationships
    product_links = relationship('ProductCategory', back_populates='category', cascade='all, delete-orphan')
    products = relationship(
        'Product',
        secondary='product_categories',
        back_populates='categories',
        viewonly=True
    )


class Product(BaseModel):
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), unique=True, index=True)
    description = Column(Text)
    image_url = Column(String(500))
    unit_of_measure = Column(String(50))

    # Relationships
    batches = relationship('ProductBatch', back_populates='product', cascade='all, delete-orphan')
    
    raw_material_links = relationship('ProductCrop', back_populates='product', cascade='all, delete-orphan')
    raw_materials = relationship('Crop', secondary='product_crops', back_populates='products', viewonly=True)

    amount_ledger = relationship("ProductAmountLedger", back_populates="product", cascade='all, delete-orphan')
    price_ledger = relationship("ProductPriceLedger", back_populates="product", cascade='all, delete-orphan')

    category_links = relationship('ProductCategory', back_populates='product', cascade='all, delete-orphan')
    categories = relationship(
        'Category',
        secondary='product_categories',
        back_populates='products',
        viewonly=True
    )

    tax_links = relationship('ProductTax', back_populates='product', cascade='all, delete-orphan')
    taxes = relationship(
        'Tax',
        secondary='product_taxes',
        back_populates='products',
        viewonly=True
    )

    @hybrid_property
    def available_amount(self):
        total = 0
        for batch in self.batches:
            total += batch.available_quantity or 0
        return total

    @available_amount.expression
    def available_amount(cls):
        """SQL expression for available amount calculation"""
        return (
            select(func.coalesce(func.sum(ProductBatch.available_quantity), 0))
            .where(ProductBatch.product_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )

class ProductCategory(BaseModel):
    __tablename__ = "product_categories"
    
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    category_id = Column(PG_UUID(as_uuid=True), ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)

    product = relationship('Product', back_populates='category_links')
    category = relationship('Category', back_populates='product_links')


class ProductBatch(BaseModel):
    __tablename__ = "product_batches"

    batch_number = Column(String(100), nullable=False, index=True)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    warehouse_id = Column(PG_UUID(as_uuid=True), ForeignKey('warehouses.id', ondelete='CASCADE'), nullable=False)

    quantity = Column(Numeric(12, 4), default=0.0)
    reserved_quantity = Column(Numeric(12, 4), default=0.0)
    cost_price = Column(Numeric(12, 4), default=0.0)
    selling_price = Column(Numeric(12, 4), default=0.0)

    manufacture_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    received_date = Column(DateTime, default=datetime.now(timezone.utc))

    notes = Column(Text, nullable=True)

    created_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    modified_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="batches")    
    warehouse_stocks = relationship('ProductWarehouse', back_populates='batch', cascade='all, delete-orphan')
    amount_transactions = relationship("ProductAmountLedger", back_populates="batch", cascade='all, delete-orphan')
    
    creator = relationship("UserModel", foreign_keys=[created_by])
    modifier = relationship("UserModel", foreign_keys=[modified_by])

    @hybrid_property
    def available_quantity(self):
        """
        Available quantity = total quantity - reserved quantity
        """
        return (self.quantity or Decimal('0.0')) - (self.reserved_quantity or Decimal('0.0'))

    @available_quantity.expression
    def available_quantity(cls):
        """
        SQL expression for available quantity
        """
        return func.coalesce(cls.quantity, 0) - func.coalesce(cls.reserved_quantity, 0)
class ProductTax(BaseModel):
    __tablename__ = "product_taxes"
    
    product_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('products.id', ondelete='CASCADE'), 
        primary_key=True
    )
    tax_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('tax.id', ondelete='CASCADE'), 
        primary_key=True
    )
    
    # Relationships
    product = relationship('Product', back_populates='tax_links')
    tax = relationship('Tax', back_populates='product_tax_links')


class ProductCrop(BaseModel):
    __tablename__ = "product_crops"

    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    crop_id = Column(PG_UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), primary_key=True)

    quantity_ratio = Column(Numeric(10, 4), default=1.0)
    is_primary = Column(Boolean, default=False)

    # Relationships
    product = relationship('Product', back_populates='raw_material_links', viewonly=True)
    crop = relationship('Crop', back_populates='product_crop',viewonly=True)


class ProductWarehouse(BaseModel):
    __tablename__ = 'product_warehouse'

    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    warehouse_id = Column(PG_UUID(as_uuid=True), ForeignKey('warehouses.id', ondelete='CASCADE'), primary_key=True)
    batch_id = Column(PG_UUID(as_uuid=True), ForeignKey('product_batches.id', ondelete='CASCADE'), primary_key=True)

    available_quantity = Column(Numeric(12, 4), default=0.0)
    reserved_quantity = Column(Numeric(12, 4), default=0.0)
    minimum_stock = Column(Numeric(12, 4), default=0.0)
    maximum_stock = Column(Numeric(12, 4), nullable=True)
    location_code = Column(String(50), nullable=True)


    batch = relationship('ProductBatch', back_populates='warehouse_stocks')


class ProductAmountLedger(BaseModel):
    __tablename__ = "product_amount_ledger"

    transaction_type = Column(Enum(TransactionType), nullable=False)
    transaction_reference = Column(String(100), nullable=True)

    quantity_change = Column(Numeric(12, 4), nullable=False)
    quantity_before = Column(Numeric(12, 4), default=0.0)
    quantity_after = Column(Numeric(12, 4), default=0.0)

    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(PG_UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    batch_id = Column(PG_UUID(as_uuid=True), ForeignKey("product_batches.id"), nullable=True)

    reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    created_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    approved_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="amount_ledger")
    batch = relationship("ProductBatch", back_populates="amount_transactions")
    warehouse = relationship("Warehouse", back_populates="amount_transactions")
    
    creator = relationship("UserModel", foreign_keys=[created_by])
    approver = relationship("UserModel", foreign_keys=[approved_by])


class ProductPriceLedger(BaseModel):
    __tablename__ = "product_price_ledger"

    previous_price = Column(Numeric(12, 4), default=0.0)
    new_price = Column(Numeric(12, 4), default=0.0)

    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    reason = Column(String(255), nullable=False)

    created_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    approved_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="price_ledger")
    creator = relationship("UserModel", foreign_keys=[created_by])
    approver = relationship("UserModel", foreign_keys=[approved_by])