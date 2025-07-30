from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.container import get_container
from app.modules.products.schemas import ProductCreate, Product, ProductList, ProductUpdate, GRNRequest, DepleteRequest

router = APIRouter(prefix="/product", tags=["Products"])

container = get_container()
product_service = container.resolve("product_service")


@router.get("", response_model=ProductList)
def get_all_products():
    return product_service.get_all_products()

@router.get("/details")
def get_product_details(id: UUID):
    return product_service.get_product_by_id(id)

@router.post("")
def create_product(product: ProductCreate):
    return product_service.create_product(product)

@router.put("")
def update_product(product: ProductUpdate):
    return product_service.update_product(product)

@router.put("/recieve")
def receive_product(product: GRNRequest):
    return product_service.receive_product(product)