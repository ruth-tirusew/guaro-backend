from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from .models import Product, ProductAmountLedger, ProductPriceLedger, ProductWarehouse
from .interface import IProductRepository

class ProductRepository(IProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: UUID) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id, Product.is_deleted == False).first()

    def list(self) -> List[Product]:
        return self.db.query(Product).filter(Product.is_deleted == False).all()

    def create(self, product: Product) -> Product:
        try:
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Product creation failed")

    def update(self, product_id: UUID, product: Product) -> Product:
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")
        try:
            for key, value in vars(product).items():
                if key.startswith('_') or key == 'id':
                    continue
                if hasattr(db_product, key):
                    setattr(db_product, key, value)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Product update failed")

    def delete(self, product_id: UUID) -> None:
        db_product = self.get(product_id)
        if db_product:
            db_product.is_deleted = True
            self.db.commit()
        else:
            raise ValueError("Product not found")

    def update_price(self, product_id: UUID, new_price: float) -> Product:
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")
        
        price_ledger = ProductPriceLedger(
            previous_price = db_product.available_price,
            updated_price  = new_price,
            product_id = product_id
        )
        
        db_product.price = new_price
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def receive(self, product_id: UUID, amount: float) -> Product:
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")

        amount_ledger = ProductAmountLedger(
            previous_amount = db_product.available_amount,
            updated_amount  = db_product.available_amount + amount,
            product_id = product_id
        )
        db.add(amount_ledger)
        db_product.available_amount += amount
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def deplete(self, product_id: UUID, amount: float) -> Product:
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")

        amount_ledger = ProductAmountLedger(
            previous_amount = db_product.available_amount,
            updated_amount  = db_product.available_amount - amount,
            product_id = product_id
        )

        db.add(amount_ledger)
        
        db_product.available_amount -= amount
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def add_product_to_warehouse(self, product_id: str, warehouse_id: str) -> Product:
        product_uuid = UUID(product_id)
        warehouse_uuid = UUID(warehouse_id)
        existing = self.db.query(ProductWarehouse).filter_by(product_id=product_uuid, warehouse_id=warehouse_uuid).first()
        if not existing:
            db_product_warehouse = ProductWarehouse(product_id=product_uuid, warehouse_id=warehouse_uuid)
            self.db.add(db_product_warehouse)
            self.db.commit()

    def remove_product_from_warehouse(self, product_id: str, warehouse_id: str) -> Product:
        product_uuid = UUID(product_id)
        warehouse_uuid = UUID(warehouse_id)
        existing = self.db.query(ProductWarehouse).filter_by(product_id=product_uuid, warehouse_id=warehouse_uuid).first()
        if not existing:
            existing.is_deleted = True
            self.db.commit()

        raise ValueError("Product not found")

    def search(self, query: str) -> List[Product]:
        return self.db.query(Product).filter(
            Product.is_deleted == False,
            or_(
                Product.name.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%")
            )
        ).all()
