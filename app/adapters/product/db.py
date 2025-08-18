from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from datetime import datetime, timezone
from app.adapters.product.models import (
    Product, ProductBatch, ProductAmountLedger, ProductPriceLedger, 
    ProductWarehouse, ProductCrop, Category, ProductCategory, TransactionType
)
from app.adapters.product.interface import IProductRepository
from app.logging import logger

class ProductRepository(IProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_category(self, category_id: UUID) -> Optional[Category]:
        """Get a single category by ID"""
        return self.db.query(Category).filter(
            Category.id == category_id, 
            Category.is_deleted == False
        ).first()

    def list_category(self) -> List[Category]:
        """List all categories"""
        return self.db.query(Category).filter(Category.is_deleted == False).all()

    def create_category(self, category: dict) -> Category:
        """Create a new category"""
        try:
            db_category = Category(**category)
            self.db.add(db_category)
            self.db.commit()
            self.db.refresh(db_category) 
            return db_category
        except IntegrityError as e:
            logger.error(f"Failed to create category {str(e)}")
            self.db.rollback()
            raise ValueError(str(e))  

    def update_category(self, category_id: UUID, category: dict) -> Optional[Category]:
        """Update an existing category"""
        db_category = self.get_category(category_id)
        if not db_category:
            raise ValueError("Category not found")
        try:
            for key, value in category.items():
                if key.startswith('_') or key == 'id':
                    continue
                if hasattr(db_category, key):
                    setattr(db_category, key, value)
            self.db.commit()
            self.db.refresh(db_category)
            return db_category
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Category update failed")

    def delete_category(self, category_id: UUID) -> None:
        """Soft delete a category"""
        db_category = self.get_category(category_id)
        if db_category:
            db_category.is_deleted = True
            self.db.commit()
        else:
            raise ValueError("Category not found")

    def search_categories(self, query: str) -> List[Category]:
        """Search categories by name or description"""
        return self.db.query(Category).filter(
            Category.is_deleted == False,
            or_(
                Category.name.ilike(f"%{query}%"),
                Category.description.ilike(f"%{query}%") if hasattr(Category, 'description') else True
            )
        ).all()

    def add_product_to_category(self, product_id: UUID, category_id: UUID) -> None:
        """Add a product to a category"""
        existing = self.db.query(ProductCategory).filter_by(
            product_id=product_id, 
            category_id=category_id
        ).first()
        
        if not existing:
            db_product_category = ProductCategory(
                product_id=product_id, 
                category_id=category_id
            )
            self.db.add(db_product_category)
            self.db.commit()

    def remove_product_from_category(self, product_id: UUID, category_id: UUID) -> None:
        """Remove a product from a category"""
        existing = self.db.query(ProductCategory).filter_by(
            product_id=product_id, 
            category_id=category_id
        ).first()
        
        if existing:
            existing.is_deleted=True
            self.db.commit()
        else:
            raise ValueError("Product-Category relationship not found")

    def get_products_by_category(self, category_id: UUID) -> List[Product]:
        """Get all products in a specific category"""
        return self.db.query(Product).join(ProductCategory).filter(
            ProductCategory.category_id == category_id,
            Product.is_deleted == False
        ).all()

    def get_categories_by_product(self, product_id: UUID) -> List[Category]:
        """Get all categories for a specific product"""
        return self.db.query(Category).join(ProductCategory).filter(
            ProductCategory.product_id == product_id,
            Category.is_deleted == False
        ).all()

    def get(self, product_id: UUID) -> Optional[Product]:
        return self.db.query(Product).filter(
            Product.id == product_id, 
            Product.is_deleted == False
        ).options(
            joinedload(Product.raw_materials),
            joinedload(Product.batches),
            joinedload(Product.categories)
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
            logger.error(f"Failed to create product {str(e)}")
            self.db.rollback()
            raise ValueError(str(e))

    def update(self, product_id: UUID, product: dict) -> Product:
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")
        try:
            for key, value in product.items():
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

    def create_batch(self, batch_data: dict) -> ProductBatch:
        """Create a new product batch"""
        try:
            batch_data['received_date'] = batch_data.get('received_date', datetime.now(timezone.utc))
            db_batch = ProductBatch(**batch_data)
            self.db.add(db_batch)
            self.db.commit()
            self.db.refresh(db_batch)
            return db_batch
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))

    def get_batch(self, batch_id: UUID) -> Optional[ProductBatch]:
        """Get a product batch by ID"""
        return self.db.query(ProductBatch).filter(
            ProductBatch.id == batch_id,
            ProductBatch.is_deleted == False
        ).first()

    def get_batches_by_product(self, product_id: UUID, warehouse_id: Optional[UUID] = None) -> List[ProductBatch]:
        """Get all batches for a product, optionally filtered by warehouse"""
        query = self.db.query(ProductBatch).filter(
            ProductBatch.product_id == product_id,
            ProductBatch.is_deleted == False
        )
        
        if warehouse_id:
            query = query.filter(ProductBatch.warehouse_id == warehouse_id)
            
        return query.all()

    def update_batch_quantities(self, batch_id: UUID, available_qty: float, reserved_qty: float = None) -> ProductBatch:
        """Update batch quantities"""
        db_batch = self.get_batch(batch_id)
        if not db_batch:
            raise ValueError("Batch not found")
        
        db_batch.available_quantity = available_qty
        if reserved_qty is not None:
            db_batch.reserved_quantity = reserved_qty
        
        db_batch.quantity = db_batch.available_quantity - db_batch.reserved_quantity
        
        self.db.commit()
        self.db.refresh(db_batch)
        return db_batch

    def reserve(self, product_id: UUID, amount: float) -> ProductBatch:
        """Update batch quantities"""
        db_batch = self.get_batch(product_id)
        if not db_batch:
            raise ValueError("Batch not found")

        db_batch.quantity = db_batch.available_quantity - amount
        db_batch.reserved_quantity = db_batch.reserved_quantity + amount
        
        self.db.commit()
        self.db.refresh(db_batch)
        return db_batch

    def update_price(self, product_id: UUID, new_price: float, reason: str, created_by: UUID, approved_by: Optional[UUID] = None) -> Product:
        """Update product price with proper ledger tracking"""
        db_product = self.get(product_id)
        if not db_product:
            raise ValueError("Product not found")
        
        current_price = 0.0
        latest_batch = self.db.query(ProductBatch).filter(
            ProductBatch.product_id == product_id,
            ProductBatch.is_deleted == False
        ).order_by(ProductBatch.created_at.desc()).first()
        
        if latest_batch:
            current_price = float(latest_batch.selling_price)
        
        price_ledger = ProductPriceLedger(
            previous_price=current_price,
            new_price=new_price,
            product_id=product_id,
            reason=reason,
            created_by=created_by,
            approved_by=approved_by
        )
        
        self.db.add(price_ledger)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def create_amount_transaction(self, transaction_data: dict) -> ProductAmountLedger:
        """Create an amount ledger transaction"""
        try:
            required_fields = ['transaction_type', 'quantity_change', 'product_id', 'warehouse_id', 'created_by']
            for field in required_fields:
                if field not in transaction_data:
                    raise ValueError(f"Missing required field: {field}")
            
            if transaction_data.get('batch_id'):
                last_transaction = self.db.query(ProductAmountLedger).filter(
                    ProductAmountLedger.product_id == transaction_data['product_id'],
                    ProductAmountLedger.warehouse_id == transaction_data['warehouse_id'],
                    ProductAmountLedger.batch_id == transaction_data['batch_id'],
                    ProductAmountLedger.is_deleted == False
                ).order_by(ProductAmountLedger.created_at.desc()).first()
            else:
                last_transaction = self.db.query(ProductAmountLedger).filter(
                    ProductAmountLedger.product_id == transaction_data['product_id'],
                    ProductAmountLedger.warehouse_id == transaction_data['warehouse_id'],
                    ProductAmountLedger.is_deleted == False
                ).order_by(ProductAmountLedger.created_at.desc()).first()
            
            quantity_before = float(last_transaction.quantity_after) if last_transaction else 0.0
            quantity_change = float(transaction_data['quantity_change'])
            quantity_after = quantity_before + quantity_change
            
            if quantity_change < 0 and quantity_after < 0:
                raise ValueError("Insufficient stock available")
            
            transaction_data['quantity_before'] = quantity_before
            transaction_data['quantity_after'] = quantity_after
            
            db_transaction = ProductAmountLedger(**transaction_data)
            self.db.add(db_transaction)
            
            if transaction_data.get('batch_id'):
                batch = self.get_batch(transaction_data['batch_id'])
                if batch:
                    batch.available_quantity = quantity_after
                    batch.quantity = batch.available_quantity + float(batch.reserved_quantity)
            
            self.db.commit()
            self.db.refresh(db_transaction)
            return db_transaction
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))

        except Exception as e:
            self.db.rollback()
            raise e

    def receive(self, product_id: UUID, amount: float, warehouse_id: UUID, batch_id: Optional[UUID] = None, 
                created_by: UUID = None, transaction_reference: str = None, notes: str = None) -> Product:
        """Receive stock (increase inventory)"""
        transaction_data = {
            'transaction_type': TransactionType.PURCHASE,
            'quantity_change': amount,
            'product_id': product_id,
            'warehouse_id': warehouse_id,
            'batch_id': batch_id,
            'created_by': created_by,
            'transaction_reference': transaction_reference,
            'notes': notes,
            'reason': 'Stock received'
        }
        
        self.create_amount_transaction(transaction_data)
        return self.get(product_id)

    def deplete(self, product_id: UUID, amount: float, warehouse_id: UUID, batch_id: Optional[UUID] = None,
                created_by: UUID = None, transaction_reference: str = None, notes: str = None) -> Product:
        """Deplete stock (decrease inventory)"""
        transaction_data = {
            'transaction_type': TransactionType.SALE,
            'quantity_change': -amount, 
            'product_id': product_id,
            'warehouse_id': warehouse_id,
            'batch_id': batch_id,
            'created_by': created_by,
            'transaction_reference': transaction_reference,
            'notes': notes,
            'reason': 'Stock depleted'
        }
        
        self.create_amount_transaction(transaction_data)
        return self.get(product_id)

    def add_product_to_warehouse(self, product_id: UUID, warehouse_id: UUID, batch_id: UUID, 
                                minimum_stock: float = 0.0, maximum_stock: Optional[float] = None,
                                location_code: Optional[str] = None) -> None:
        """Add a product batch to a warehouse"""
        existing = self.db.query(ProductWarehouse).filter_by(
            product_id=product_id, 
            warehouse_id=warehouse_id,
            batch_id=batch_id
        ).first()
        
        if not existing:
            db_product_warehouse = ProductWarehouse(
                product_id=product_id, 
                warehouse_id=warehouse_id,
                batch_id=batch_id,
                minimum_stock=minimum_stock,
                maximum_stock=maximum_stock,
                location_code=location_code
            )
            self.db.add(db_product_warehouse)
            self.db.commit()

    def remove_product_from_warehouse(self, product_id: UUID, warehouse_id: UUID, batch_id: UUID) -> None:
        """Remove a product batch from a warehouse"""
        existing = self.db.query(ProductWarehouse).filter_by(
            product_id=product_id, 
            warehouse_id=warehouse_id,
            batch_id=batch_id
        ).first()
        
        if existing:
            
            existing.is_deleted=True
            self.db.commit()
        else:
            raise ValueError("Product-Warehouse-Batch relationship not found")

    def get_warehouse_stock(self, product_id: UUID, warehouse_id: UUID, batch_id: Optional[UUID] = None) -> List[ProductWarehouse]:
        """Get warehouse stock for a product"""
        query = self.db.query(ProductWarehouse).filter(
            ProductWarehouse.product_id == product_id,
            ProductWarehouse.warehouse_id == warehouse_id
        )
        
        if batch_id:
            query = query.filter(ProductWarehouse.batch_id == batch_id)
            
        return query.all()

    def search(self, query: str) -> List[Product]:
        """Search products by name, SKU, or description"""
        return self.db.query(Product).filter(
            Product.is_deleted == False,
            or_(
                Product.name.ilike(f"%{query}%"),
                Product.sku.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%")
            )
        ).all()
    

    def add_product_crop(self, product_id: UUID, crop_id: UUID, quantity_ratio: float = 1.0) -> ProductCrop:
        """Add a crop as raw material to a product"""
        try:
            existing = self.db.query(ProductCrop).filter_by(
                product_id=product_id,
                crop_id=crop_id
            ).first()
            
            if existing:
                raise ValueError("Product-Crop relationship already exists")
            
            db_product_crop = ProductCrop(
                product_id=product_id,
                crop_id=crop_id,
                quantity_ratio=quantity_ratio,
                is_primary=is_primary
            )
            self.db.add(db_product_crop)
            self.db.commit()
            self.db.refresh(db_product_crop)
            return db_product_crop
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))

    def remove_product_crop(self, product_id: UUID, crop_id: UUID) -> None:
        """Remove a crop from a product's raw materials"""
        existing = self.db.query(ProductCrop).filter_by(
            product_id=product_id, 
            crop_id=crop_id
        ).first()
        
        if existing:
            existing.is_deleted=True
            self.db.commit()
        else:
            raise ValueError("Product-Crop relationship not found")

    def get_product_crops(self, product_id: UUID) -> List[ProductCrop]:
        """Get all crops used in a product"""
        return self.db.query(ProductCrop).filter(
            ProductCrop.product_id == product_id
        ).all()

    def update_product_crop_ratio(self, product_id: UUID, crop_id: UUID, new_ratio: float) -> ProductCrop:
        """Update the quantity ratio for a product-crop relationship"""
        existing = self.db.query(ProductCrop).filter_by(
            product_id=product_id,
            crop_id=crop_id
        ).first()
        
        if not existing:
            raise ValueError("Product-Crop relationship not found")
        
        existing.quantity_ratio = new_ratio
        self.db.commit()
        self.db.refresh(existing)
        return existing