from app.adapters.product.interface import IProductRepository

from app.modules.warehouse.service import WarehouseService


class ProductService:
    def __init__(self, product_repository: IProductRepository, warehouse_service: WarehouseService):
        self.repository = product_repository
        self.warehouse_service = warehouse_service