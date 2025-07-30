from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from app.adapters.product.models import Product, ProductAmountLedger, ProductPriceLedger, ProductWarehouse, ProductCrop
from app.adapters.product.interface import IProductRepository

class ProductRepository(IProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: UUID) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id, Product.is_deleted == False).options(
                joinedload(Product.raw_materials),
                joinedload(Product.warehouses)
            ).first()

    def list(self) -> List[Product]:
        return self.db.query(Product).filter(Product.is_deleted == False).all()

    def create(self, product: dict) -> Product:
        try:
            db_product = Product(**product)
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except IntegrityError as e:
            print(e)
            self.db.rollback()
            raise ValueError(e._message())

    def update(self, product_id: UUID, product: dict) -> Product:
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")
        try:
            for key, value in product.items():  # Directly iterate over the dictionary
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
            previous_price = db_product.price,
            updated_price  = new_price,
            product_id = product_id
        )
        
        db_product.price = new_price
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def receive(self, product_id: UUID, amount: float, warehouse_id: UUID) -> Product:
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")
        product_ledger = self.db.query(ProductAmountLedger).filter(
            ProductAmountLedger.is_deleted == False, 
            ProductAmountLedger.product_id==product_id,
            ProductAmountLedger.warehouse_id==warehouse_id
            ).first()

        available_amount =  0
        if product_ledger:
            available_amount=product_ledger.available_amount
        amount_ledger = ProductAmountLedger(
            previous_amount = available_amount,
            updated_amount  = available_amount + amount,
            warehouse_id = warehouse_id,
            product_id = product_id
        )
        self.db.add(amount_ledger)
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
    
    def add_product_crop(self, data:dict):
        try:
            
            db_product_crop = ProductCrop(**data)
            self.db.add(db_product_crop)
            self.db.commit()
            self.db.refresh(db_product_crop)

        except Exception as e:
            print(e)
            self.db.rollback()
            raise ValueError(e) 

    def remove_product_crop(self, data:dict):
        try:
            raw_material = self.db.query(ProductCrop).filter_by(product_id=data.get("product_id"), crop_id=data.get("crop_id"))
            raw_material.is_deleted = True
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise ValueError(e)