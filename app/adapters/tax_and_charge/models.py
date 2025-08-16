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
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


from app.models.base import BaseModel

class TaxType(str, SQLEnum):
    EMPLOYEE_TAX = "EMPLOYEE_TAX"
    PART_TIME = "PART_TIME"
    CONTRACTOR = "CONTRACTOR"
    PRODUCT_TAX="PRODUCT_TAX"
    TOT="TOT"
    COMPANY_PROFIT_TAX="COMPANY_PROFIT_TAX"
    WITHHOLDING_TAX="WITHHOLDING_TAX"
    PROFIT_TAX="PROFIT_TAX"


class Tax(BaseModel):
    __tablename__ = "tax"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tax_percentage: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    is_compound: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    product_tax_links = relationship('ProductTax', back_populates='tax', cascade='all, delete-orphan')
    products = relationship(
        'Product',
        secondary='product_taxes',
        back_populates='taxes',
        viewonly=True
    )
