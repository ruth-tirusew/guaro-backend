import re
import uuid
from pydantic import BaseModel, EmailStr, field_validator, model_validator, ValidationInfo, HttpUrl
from typing import List, Optional, Any

# Base Models
class ProductBase(BaseModel):
    image_url: Optional[HttpUrl]=None
    name: str
    sku: Optional[str]
    description: Optional[str] = None
    unit_of_measure: str


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class Category(CategoryBase):
    id: uuid.UUID
    model_config = {"from_attributes": True}

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    id: uuid.UUID

class CategoryDetail(CategoryBase):
    id: uuid.UUID
    products: Optional[List['Product']] = []
    model_config = {"from_attributes": True}

class CategoryList(BaseModel):
    categories: List[Category]

# Product Schemas
class Product(ProductBase):
    id: uuid.UUID
    available_amount: Optional[float] = 0
    categories: Optional[List[Category]] = []
    model_config = {"from_attributes": True}

class ProductUpdate(ProductBase):
    id: uuid.UUID
    price: Optional[float] = None
    raw_materials: List[uuid.UUID]
    categories: Optional[List[uuid.UUID]] = []

class ProductCreate(ProductBase):
    raw_materials: Optional[List[uuid.UUID]] = []
    categories: Optional[List[uuid.UUID]] = []

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
    id: uuid.UUID
    # warehouses: List[Warehouse]
    raw_materials: List[Crop]
    categories: List[Category]
    model_config = {"from_attributes": True}

class ProductList(BaseModel):
    products: List[Product]

class BatchInfo(BaseModel):
    id: Optional[str]=None
    batch_number: Optional[str] = None
    quantity: Optional[float]=None
    available_quantity: Optional[float]=None
    reserved_quantity: Optional[float]=None
    cost_price: Optional[float]=None
    selling_price: Optional[float]=None
    warehouse_id: Optional[uuid.UUID]=None
    expiry_date: Optional[Any] = None
    manufacture_date: Optional[Any] = None
    received_date: Optional[Any] = None
    notes: Optional[str] = None

class GRNRequest(BaseModel):
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    amount: float
    cost_price: Optional[float]=None
    selling_price: Optional[float]=None
    warehouse_id: Optional[uuid.UUID]=None
    expiry_date: Optional[Any] = None
    manufacture_date: Optional[Any] = None
    notes: Optional[str] = None


class ProductCategoryLink(BaseModel):
    product_id: uuid.UUID
    category_id: uuid.UUID

class ProductCategoryRequest(BaseModel):
    product_id: uuid.UUID
    category_id: uuid.UUID

class ProductSearchRequest(BaseModel):
    query: str
    category_id: Optional[uuid.UUID] = None

class CategorySearchRequest(BaseModel):
    query: str

class ProductResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Product] = None

class CategoryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Category] = None

class ProductListResponse(BaseModel):
    success: bool
    message: str
    data: ProductList

class CategoryListResponse(BaseModel):
    success: bool
    message: str
    data: CategoryList
