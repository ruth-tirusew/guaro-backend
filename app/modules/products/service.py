from uuid import UUID

from app.adapters.product.interface import IProductRepository

from app.core.exceptions import ErrorFactory

from app.modules.products.schemas import (
    ProductList, ProductCreate, Product, ProductDetail, ProductUpdate,
    GRNRequest, DepleteRequest
    )
from app.modules.biodata.service import BiodataService
from app.modules.warehouse.service import WarehouseService


class ProductService:
    def __init__(self, product_repository: IProductRepository, crop_service: BiodataService,warehouse_service: WarehouseService):
        self.repository = product_repository
        self.warehouse_service = warehouse_service
        self.crop_service = crop_service

    def get_all_products(self)->ProductList:
        products = self.repository.list()
        return ProductList(products = [Product.from_orm(p) for p in products])

    def get_product_by_id(self, id:UUID)->ProductDetail:
        product = self.repository.get(id)
        return ProductDetail.from_orm(product)

    def create_product(self,product:ProductCreate):
        product_dict = {
                "image": product.image,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "unit": product.unit
        }        
        saved_product = self.repository.create(product_dict)
        for r in product.raw_materials:
            raw_material = {
                "crop_id": r,
                "product_id": saved_product.id
            }
            self.repository.add_product_crop(raw_material)

        return saved_product
    
    def update_product(self, product: ProductUpdate):
        existing_product = self.get_product_by_id(product.id)
        if not existing_product:
            raise ErrorFactory.not_found("Product")
        product_dict = {
                "image": product.image,
                "name": product.name,
                "description": product.description,
                "unit": product.unit
        }
        if product.price:
            self.repository.update_price(product.id, product.price)

        for r in existing_product.raw_materials:
            removed_raw_material = {
                "crop_id": r,
                "product_id": existing_product.id
            }
            self.repository.remove_product_crop(removed_raw_material)

        for r in product.raw_materials:
            raw_material = {
                "crop_id": r,
                "product_id": existing_product.id
            }
            self.repository.add_product_crop(raw_material)

        saved_product = self.repository.update(product.id, product_dict)
        return ProductDetail.from_orm(saved_product) 

    def receive_product(self,request: GRNRequest) -> Product:
        product = self.repository.receive(request.product_id, request.amount, request.warehouse_id)
        return product
