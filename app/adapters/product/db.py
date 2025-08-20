from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from datetime import datetime, timezone
from app.adapters.product.models import (
    Product, ProductBatch, ProductAmountLedger, ProductPriceLedger, 
    ProductWarehouse, ProductCrop, Category, ProductCategory, ProductTax, TransactionType
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

    def reserve(self, product_id: UUID, amount: float, warehouse_id: Optional[UUID] = None, batch_id: Optional[UUID] = None, created_by: Optional[UUID] = None) -> ProductBatch:
        """
        Reserve stock from a specific batch or from available batches
        Moves quantity from available to reserved
        """
        if batch_id:
            batch = self.get_batch(batch_id)
            if not batch:
                raise ValueError("Batch not found")
        else:
            batches = self.get_batches_by_product(product_id, warehouse_id)
            available_batches = [b for b in batches if b.available_quantity >= amount]
            if not available_batches:
                raise ValueError("Insufficient available stock")
            batch = sorted(available_batches, key=lambda x: x.received_date)[0]
        
        available = Decimal(str(batch.available_quantity))
        if available < Decimal(str(amount)):
            raise ValueError(f"Insufficient available stock. Available: {available}, Requested: {amount}")
        
        new_reserved = Decimal(str(batch.reserved_quantity)) + Decimal(str(amount))
        batch.reserved_quantity = float(new_reserved)

        self.db.commit()
        self.db.refresh(batch)
        return batch

    def deplete(self, product_id: UUID, amount: float, warehouse_id: UUID, batch_id: Optional[UUID] = None,
                created_by: Optional[UUID] = None, transaction_reference: Optional[str] = None, notes: Optional[str] = None) -> Product:
        """
        Deplete stock from a specific batch
        Reduces reserved quantity (assumes stock was already reserved)
        """
        if batch_id:
            batch = self.get_batch(batch_id)
            if not batch:
                raise ValueError("Batch not found")
        else:
            batches = self.get_batches_by_product(product_id, warehouse_id)
            reserved_batches = [b for b in batches if b.reserved_quantity >= amount]
            if not reserved_batches:
                raise ValueError("No batch found with sufficient reserved stock")
            batch = reserved_batches[0]
        
        reserved = Decimal(str(batch.reserved_quantity))
        if reserved < Decimal(str(amount)):
            raise ValueError(f"Insufficient reserved stock. Reserved: {reserved}, Requested: {amount}")
        
        new_reserved = reserved - Decimal(str(amount))
        new_total = Decimal(str(batch.quantity)) - Decimal(str(amount))
        
        batch.reserved_quantity = float(new_reserved)
        batch.quantity = float(new_total)

        self.db.commit()
        self.db.refresh(batch)
        return self.get(product_id)

    def unreserve(self, batch_id: UUID, amount: float, created_by: Optional[UUID] = None) -> ProductBatch:
        """
        Unreserve stock from a specific batch
        Moves quantity from reserved back to available
        """
        batch = self.get_batch(batch_id)
        if not batch:
            raise ValueError("Batch not found")
        
        reserved = Decimal(str(batch.reserved_quantity))
        if reserved < Decimal(str(amount)):
            raise ValueError(f"Insufficient reserved stock. Reserved: {reserved}, Requested: {amount}")
        
        new_reserved = reserved - Decimal(str(amount))
        batch.reserved_quantity = float(new_reserved)
        
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def update_batch_quantities(self, batch_id: UUID, reserved_qty: float = None) -> ProductBatch:
        """Update batch quantities with validation"""
        batch = self.get_batch(batch_id)
        if not batch:
            raise ValueError("Batch not found")
        
        if reserved_qty is not None and reserved_qty < 0:
            raise ValueError("Reserved quantity cannot be negative")
        
        if reserved_qty is not None:
            batch.reserved_quantity = reserved_qty
                
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def update_price(self, product_id: UUID, new_price: float, reason: Optional[str] = None, created_by: Optional[UUID] = None, approved_by: Optional[UUID] = None) -> Product:
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
            reason=reason or "Price update",
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
            
            self.db.commit()
            self.db.refresh(db_transaction)
            return db_transaction
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except Exception as e:
            self.db.rollback()
            raise e

    def receive(self, product_id: UUID, amount: float, warehouse_id: UUID, batch_info: Optional[dict] = None, 
                created_by: Optional[UUID] = None, transaction_reference: Optional[str] = None, notes: Optional[str] = None) -> Product:
        """Receive stock (increase inventory)"""
        batch_id = None
        
        if batch_info:
            if 'batch_id' in batch_info and batch_info['batch_id']:
                batch_id = batch_info['batch_id']
                batch = self.get_batch(batch_id)
                if batch:
                    batch.quantity = float(Decimal(str(batch.quantity)) + Decimal(str(amount)))
                    self.db.commit()
            else:
                batch_data = {
                    'product_id': product_id,
                    'warehouse_id': warehouse_id,
                    'quantity': amount,
                    'created_by': created_by,
                    **batch_info
                }
                batch = self.create_batch(batch_data)
                batch_id = batch.id
        
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

    def add_product_to_warehouse(self, product_id: UUID, warehouse_id: UUID, batch_id: Optional[UUID] = None, 
                                minimum_stock: float = 0.0, maximum_stock: Optional[float] = None,
                                location_code: Optional[str] = None) -> Product:
        """Add a product batch to a warehouse"""
        if not batch_id:
            raise ValueError("batch_id is required")
            
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
        
        return self.get(product_id)

    def remove_product_from_warehouse(self, product_id: UUID, warehouse_id: UUID, batch_id: Optional[UUID] = None) -> Product:
        """Remove a product batch from a warehouse"""
        if batch_id:
            existing = self.db.query(ProductWarehouse).filter_by(
                product_id=product_id, 
                warehouse_id=warehouse_id,
                batch_id=batch_id
            ).first()
        else:
            existing = self.db.query(ProductWarehouse).filter_by(
                product_id=product_id, 
                warehouse_id=warehouse_id
            ).first()
        
        if existing:
            existing.is_deleted = True
            self.db.commit()
        else:
            raise ValueError("Product-Warehouse relationship not found")
            
        return self.get(product_id)

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

    def add_product_crop(self, data: dict) -> ProductCrop:
        """Add a crop as raw material to a product"""
        try:
            product_id = data.get('product_id')
            crop_id = data.get('crop_id')
            quantity_ratio = data.get('quantity_ratio', 1.0)
            is_primary = data.get('is_primary', False)
            
            if not product_id or not crop_id:
                raise ValueError("product_id and crop_id are required")
            
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

    def remove_product_crop(self, data: dict) -> None:
        """Remove a crop from a product's raw materials"""
        product_id = data.get('product_id')
        crop_id = data.get('crop_id')
        
        if not product_id or not crop_id:
            raise ValueError("product_id and crop_id are required")
            
        existing = self.db.query(ProductCrop).filter_by(
            product_id=product_id, 
            crop_id=crop_id
        ).first()
        
        if existing:
            existing.is_deleted = True
            self.db.commit()
        else:
            raise ValueError("Product-Crop relationship not found")

    def get_product_crops(self, product_id: UUID) -> List[ProductCrop]:
        """Get all crops used in a product"""
        return self.db.query(ProductCrop).filter(
            ProductCrop.product_id == product_id,
            ProductCrop.is_deleted == False
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

    def add_tax_to_product(self, product_id: UUID, tax_id: UUID) -> ProductTax:
        """Add a tax to a product"""
        try:
            existing = self.db.query(ProductTax).filter_by(
                product_id=product_id,
                tax_id=tax_id
            ).first()
            
            if existing:
                if existing.is_deleted:
                    existing.is_deleted = False
                    self.db.commit()
                    self.db.refresh(existing)
                    return existing
                else:
                    raise ValueError("Product-Tax relationship already exists")
            
            db_product_tax = ProductTax(
                product_id=product_id,
                tax_id=tax_id
            )
            self.db.add(db_product_tax)
            self.db.commit()
            self.db.refresh(db_product_tax)
            return db_product_tax
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))

    def remove_tax_from_product(self, product_id: UUID, tax_id: UUID) -> None:
        """Remove a tax from a product"""
        existing = self.db.query(ProductTax).filter_by(
            product_id=product_id,
            tax_id=tax_id
        ).first()
        
        if existing:
            existing.is_deleted = True
            self.db.commit()
        else:
            raise ValueError("Product-Tax relationship not found")

    def get_product_taxes(self, product_id: UUID) -> List[ProductTax]:
        """Get all taxes for a product"""
        return self.db.query(ProductTax).filter(
            ProductTax.product_id == product_id,
            ProductTax.is_deleted == False
        ).all()

    def get_low_stock_products(self, warehouse_id: Optional[UUID] = None) -> List[Product]:
        """Get products with stock below minimum levels"""
        query = self.db.query(Product).join(ProductBatch).join(ProductWarehouse).filter(
            Product.is_deleted == False,
            ProductBatch.available_quantity < ProductWarehouse.minimum_stock
        )
        
        if warehouse_id:
            query = query.filter(ProductWarehouse.warehouse_id == warehouse_id)
            
        return query.all()

    def get_expiring_batches(self, days_ahead: int = 30) -> List[ProductBatch]:
        """Get batches expiring within specified days"""
        from datetime import timedelta
        future_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        
        return self.db.query(ProductBatch).filter(
            ProductBatch.is_deleted == False,
            ProductBatch.expiry_date <= future_date,
            ProductBatch.expiry_date >= datetime.now(timezone.utc)
        ).all()

    def get_stock_valuation(self, warehouse_id: Optional[UUID] = None) -> dict:
        """Calculate total stock valuation"""
        query = self.db.query(ProductBatch).filter(
            ProductBatch.is_deleted == False
        )
        
        if warehouse_id:
            query = query.filter(ProductBatch.warehouse_id == warehouse_id)
        
        batches = query.all()
        total_cost_value = sum(float(batch.quantity) * float(batch.cost_price) for batch in batches)
        total_selling_value = sum(float(batch.quantity) * float(batch.selling_price) for batch in batches)
        total_quantity = sum(float(batch.quantity) for batch in batches)
        
        return {
            'total_cost_value': total_cost_value,
            'total_selling_value': total_selling_value,
            'total_quantity': total_quantity,
            'potential_profit': total_selling_value - total_cost_value
        }