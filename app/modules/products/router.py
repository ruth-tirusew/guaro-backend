from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends

from app.modules.products.schemas import ProductCreate, Product, ProductList, ProductUpdate, GRNRequest
from app.dependencies import ProductServiceDep
from app.modules.products.service import ProductService

router = APIRouter(prefix="/product", tags=["Products"])


@router.get("", response_model=ProductList)
def get_all_products(product_service: ProductServiceDep):
    return product_service.get_all_products()

@router.get("/details")
def get_product_details(id: UUID, product_service: ProductServiceDep):
    return product_service.get_product_by_id(id)

@router.post("")
def create_product(product: ProductCreate, product_service: ProductServiceDep):
    return product_service.create_product(product)

@router.put("")
def update_product(product: ProductUpdate, product_service: ProductServiceDep):
    return product_service.update_product(product)

@router.put("/recieve")
def receive_product(product: GRNRequest, product_service: ProductServiceDep):
    return product_service.receive_product(product)

@router.put("/deplete")
def deplete_product(product: GRNRequest, product_service: ProductServiceDep):
    return product_service.deplete_product(product)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id:UUID, product_service: ProductServiceDep):
    return product_service.delete_product(id)