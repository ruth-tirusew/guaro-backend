from typing import Optional, List
from uuid import UUID, uuid4
from .models import Product
from .interface import IProductRepository

class MockProductRepository(IProductRepository):
    def __init__(self):
        self.products = []
        self.products_warehouse = []

    def get(self, product_id: UUID) -> Optional[Product]:
        for product in self.products:
            if product.id == product_id and not getattr(product, 'is_deleted', False):
                return product
        return None

    def list(self) -> List[Product]:
        return [p for p in self.products if not getattr(p, 'is_deleted', False)]

    def create(self, product: Product) -> Product:
        product.id = uuid4()
        self.products.append(product)
        return product

    def update(self, product_id: UUID, product: Product) -> Product:
        for idx, p in enumerate(self.products):
            if p.id == product_id:
                self.products[idx] = product
                return product
        raise ValueError("Product not found")

    def delete(self, product_id: UUID) -> None:
        for p in self.products:
            if p.id == product_id:
                setattr(p, 'is_deleted', True)
                return
        raise ValueError("Product not found")

    def update_price(self, product_id: UUID, new_price: float) -> Product:
        product = self.get(product_id)
        if product:
            product.price = new_price
            return product
        raise ValueError("Product not found")

    def receive(self, product_id: UUID, amount: float) -> Product:
        product = self.get(product_id)
        if product:
            product.available_amount += amount
            return product
        raise ValueError("Product not found")

    def deplete(self, product_id: UUID, amount: float) -> Product:
        product = self.get(product_id)
        if product:
            product.available_amount -= amount
            return product
        raise ValueError("Product not found")


    def add_product_to_warehouse(self, product_id: str, warehouse_id: str) -> Product:
        product = self.get(product_id)
        if product:
            self.products_warehouse.append({
                "warehouse_id": warehouse_id,
                "product_id":product_id
            })
            return product
            
        raise ValueError("Product not found")

    def remove_product_from_warehouse(self, product_id: str, warehouse_id: str) -> Product:
        for idx, p in enumerate(self.products_warehouse):
            if p.get("product_id") == product_id and p.get("warehouse_id")==warehouse_id:
                self.products_warehouse.pop(p)

        raise ValueError("Product not found")

    def search(self, query: str) -> List[Product]:
        q = query.lower()
        return [p for p in self.products if not getattr(p, 'is_deleted', False) and (q in (p.name or '').lower() or q in (p.description or '').lower())] 