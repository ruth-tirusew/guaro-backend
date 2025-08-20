from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.adapters.product.models import Product, Category, ProductBatch, ProductTax

class IProductRepository(ABC):
    @abstractmethod
    def get_category(self, category_id: UUID) -> Optional[Category]:
        pass
    
    @abstractmethod
    def list_category(self, category_id: UUID) -> List[Category]:
        pass

    @abstractmethod
    def create_category(self, category: dict) -> Optional[Category]:
        pass

    @abstractmethod
    def update_category(self, category_id: UUID, category: dict) -> Category:
        pass

    @abstractmethod
    def delete_category(self, category_id: UUID) -> None:
        pass

    @abstractmethod
    def get(self, product_id: UUID) -> Optional[Product]:
        pass

    @abstractmethod
    def list(self) -> List[Product]:
        pass

    @abstractmethod
    def create(self, product: dict) -> Product:
        pass

    @abstractmethod
    def update(self, product_id: UUID, product: dict) -> Product:
        pass

    @abstractmethod
    def delete(self, product_id: UUID) -> None:
        pass

    @abstractmethod
    def update_price(self, product_id: UUID, new_price: float) -> Product:
        pass

    @abstractmethod
    def receive(self, product_id: UUID, amount: float, warehouse_id: UUID, batch_info: Optional[dict] = None) -> Product:
        pass

    @abstractmethod
    def deplete(self, product_id: UUID, amount: float, warehouse_id: UUID, batch_info: Optional[dict] = None) -> Product:
        pass

    @abstractmethod
    def reserve(self, product_id: UUID, amount: float) -> ProductBatch:
        pass
    
    @abstractmethod
    def add_product_to_warehouse(self, product_id: str, warehouse_id: str) -> Product:
        pass

    @abstractmethod
    def remove_product_from_warehouse(self, product_id: str, warehouse_id: str) -> Product:
        pass

    @abstractmethod
    def search(self, query: str) -> List[Product]:
        pass

    @abstractmethod
    def remove_product_crop(self, data: dict):
        pass

    @abstractmethod
    def add_product_crop(self, data: dict):
        pass

    @abstractmethod
    def add_tax_to_product(self, product_id: UUID, tax_id: UUID) -> ProductTax:
        pass

    @abstractmethod
    def remove_tax_from_product(self, product_id: UUID, tax_id: UUID) -> None:
        pass

    @abstractmethod
    def get_product_taxes(self, product_id: UUID) -> List[ProductTax]:
        pass