from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Boolean,
    select,
    func,
    Text
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel
from typing import Optional
import enum

class TaxType(str, enum.Enum):
    EMPLOYEE_TAX = "EMPLOYEE_TAX"
    PART_TIME = "PART_TIME"
    CONTRACTOR = "CONTRACTOR"
    PRODUCT_TAX = "PRODUCT_TAX"
    TOT = "TOT"
    COMPANY_PROFIT_TAX = "COMPANY_PROFIT_TAX"
    WITHHOLDING_TAX = "WITHHOLDING_TAX"
    PROFIT_TAX = "PROFIT_TAX"

class Tax(BaseModel):
    __tablename__ = "tax"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tax_type: Mapped[TaxType] = mapped_column(SQLEnum(TaxType, name="tax_type"), nullable=False)
    tax_percentage: Mapped[Numeric] = mapped_column(Numeric(10, 2), default=0.0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    product_tax_links = relationship('ProductTax', back_populates='tax', cascade='all, delete-orphan')
    products = relationship(
        'Product',
        secondary='product_taxes',
        back_populates='taxes',
        viewonly=True
    )