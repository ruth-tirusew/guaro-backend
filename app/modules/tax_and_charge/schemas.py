from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from decimal import Decimal
from uuid import UUID
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

class TaxBase(BaseModel):
    name: str = Field(..., max_length=100, description="Tax name")
    tax_type: TaxType = Field(..., description="Type of tax")
    tax_percentage: Decimal = Field(default=Decimal('0.0'), ge=0, le=100, description="Tax percentage")
    description: Optional[str] = Field(None, description="Tax description")

class ProductTaxBase(BaseModel):
    product_id: UUID = Field(..., description="Product ID")
    tax_id: UUID = Field(..., description="Tax ID")

class Tax(TaxBase):
    pass

class TaxCreate(TaxBase):
    pass

class TaxUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    tax_type: Optional[TaxType] = None
    tax_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    description: Optional[str] = None

class ProductTaxCreate(ProductTaxBase):
    pass

class TaxList(BaseModel):
    items: List[Tax]
    total: int
    page: int
    size: int
    pages: int
