import re
import uuid
from pydantic import BaseModel, EmailStr, field_validator, model_validator, ValidationInfo
from typing import List, Optional, Any

class ProductBase(BaseModel):
    image: str
    name: str
    description: Optional[str]=None
    price: float
    unit: str


class Product(ProductBase):
    id: uuid.UUID
    available_amount: Optional[float]=0
    model_config = {"from_attributes": True}

class ProductUpdate(ProductBase):
    id: uuid.UUID
    price:Optional[float] = None
    raw_materials: List[uuid.UUID]

class ProductCreate(ProductBase):
    raw_materials: List[uuid.UUID]

class Crop(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    variety: Optional[str] = None

    model_config = {"from_attributes": True}


class Warehouse(BaseModel):
    id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    location: str
    name: str

    model_config = {"from_attributes": True}


class ProductDetail(ProductBase):
    id:uuid.UUID
    warehouses: List[Warehouse]
    raw_materials: List[Crop]
    model_config = {"from_attributes": True}

class ProductList(BaseModel):
    products:List[Product]

class GRNRequest(BaseModel):
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    amount: float

class DepleteRequest(BaseModel):
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    amount: float
