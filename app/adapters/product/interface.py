from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.adapters.product.models import Product

class IProductRepository(ABC):
    @abstractmethod
    def get(self, product_id: UUID) -> Optional[Product]:
        pass

    @abstractmethod
    def list(self) -> List[Product]:
        pass

    @abstractmethod
    def create(self, product: Product) -> Product:
        pass

    @abstractmethod
    def update(self, product_id: UUID, product: Product) -> Product:
        pass

    @abstractmethod
    def delete(self, product_id: UUID) -> None:
        pass

    @abstractmethod
    def update_price(self, product_id: UUID, new_price: float) -> Product:
        pass

    @abstractmethod
    def receive(self, product_id: UUID, amount: float) -> Product:
        pass

    @abstractmethod
    def deplete(self, product_id: UUID, amount: float) -> Product:
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

    