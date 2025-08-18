from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from app.adapters.product.interface import IProductRepository
from app.core.exceptions import ErrorFactory
from app.modules.products.schemas import (
    ProductList, ProductCreate, Product, ProductDetail, ProductUpdate,
    GRNRequest, CategoryList, CategoryCreate, Category, CategoryDetail, CategoryUpdate
)
from app.modules.biodata.service import BiodataService
from app.modules.warehouse.service import WarehouseService

class ProductService:
    def __init__(self, product_repository: IProductRepository, crop_service: BiodataService, warehouse_service: WarehouseService):
        self.repository = product_repository
        self.warehouse_service = warehouse_service
        self.crop_service = crop_service

    def _generate_batch_number(self, product_id: UUID, warehouse_id: UUID) -> str:
        """Generate a unique batch number"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        product_code = str(product_id)[:8].upper()
        warehouse_code = str(warehouse_id)[:4].upper()
        return f"BT-{product_code}-{warehouse_code}-{timestamp}"

    def get_all_products(self) -> ProductList:
        products = self.repository.list()
        return ProductList(products=[Product.from_orm(p) for p in products])

    def get_product_by_id(self, id: UUID) -> ProductDetail:
        product = self.repository.get(id)
        if not product:
            raise ErrorFactory.not_found("Product")
        return ProductDetail.from_orm(product)

    def create_product(self, product: ProductCreate, created_by: UUID):
        """Create a new product with proper validation"""
        product_dict = {
            "image_url": product.image_url,
            "name": product.name,
            "description": product.description,
            "unit_of_measure": product.unit_of_measure,
            "sku": product.sku,
            "created_by": created_by
        }
        saved_product = self.repository.create(product_dict)
        
        # Add raw materials (crops) to product
        if hasattr(product, 'raw_materials') and product.raw_materials:
            for crop_id in product.raw_materials:
                # Validate crop exists
                crop = self.crop_service.get_crop_by_id(crop_id)
                if not crop:
                    raise ErrorFactory.not_found(f"Crop with ID {crop_id}")
                
                self.repository.add_product_crop(
                    product_id=saved_product.id,
                    crop_id=crop_id,
                    quantity_ratio=1.0,
                    is_primary=False
                )
        
        # Add product to categories
        if hasattr(product, 'categories') and product.categories:
            for category_id in product.categories:
                # Validate category exists
                self.get_category_by_id(category_id)
                self.repository.add_product_to_category(saved_product.id, category_id)
        
        return ProductDetail.from_orm(saved_product)

    def update_product(self, product: ProductUpdate, modified_by: UUID):
        """Update product with proper validation and audit trail"""
        existing_product = self.get_product_by_id(product.id)
        if not existing_product:
            raise ErrorFactory.not_found("Product")

        product_dict = {
            "image_url": product.image_url,
            "name": product.name,
            "description": product.description,
            "unit_of_measure": getattr(product, 'unit_of_measure', getattr(product, 'unit', None)),
            "sku": product.sku,
            "modified_by": modified_by
        }

        # Update price if provided
        if hasattr(product, 'price') and product.price:
            self.repository.update_price(
                product_id=product.id,
                new_price=product.price,
                reason="Price updated via product update",
                created_by=modified_by
            )

        # Update raw materials
        if hasattr(product, 'raw_materials'):
            # Remove existing raw materials
            existing_crops = self.repository.get_product_crops(product.id)
            for crop_rel in existing_crops:
                self.repository.remove_product_crop(product.id, crop_rel.crop_id)

            # Add new raw materials
            for crop_id in product.raw_materials:
                # Validate crop exists
                crop = self.crop_service.get_crop_by_id(crop_id)
                if not crop:
                    raise ErrorFactory.not_found(f"Crop with ID {crop_id}")
                
                self.repository.add_product_crop(
                    product_id=product.id,
                    crop_id=crop_id,
                    quantity_ratio=1.0,
                    is_primary=False
                )

        # Update categories
        if hasattr(product, 'categories'):
            # Remove existing categories
            existing_categories = self.repository.get_categories_by_product(product.id)
            for category in existing_categories:
                self.repository.remove_product_from_category(product.id, category.id)
            
            # Add new categories
            for category_id in product.categories:
                # Validate category exists
                self.get_category_by_id(category_id)
                self.repository.add_product_to_category(product.id, category_id)

        saved_product = self.repository.update(product.id, product_dict)
        return ProductDetail.from_orm(saved_product)

    def delete_product(self, product_id: UUID) -> None:
        """Soft delete a product"""
        existing_product = self.get_product_by_id(product_id)
        if not existing_product:
            raise ErrorFactory.not_found("Product")
        self.repository.delete(product_id)

    def search_products(self, query: str) -> ProductList:
        """Search products by name, SKU, or description"""
        products = self.repository.search(query)
        return ProductList(products=[Product.from_orm(p) for p in products])

    def receive_product(self, request: GRNRequest, created_by: UUID) -> dict:
        """
        Receive product into inventory - creates batch and updates stock
        Returns both the product and the created batch information
        """
        # Validate product exists
        product = self.get_product_by_id(request.product_id)
        if not product:
            raise ErrorFactory.not_found("Product")
        
        # Validate warehouse exists
        warehouse = self.warehouse_service.get_warehouse_by_id(request.warehouse_id)
        if not warehouse:
            raise ErrorFactory.not_found("Warehouse")

        # Generate batch number if not provided
        batch_number = None
        if hasattr(request, 'batch_info') and request.batch_info and hasattr(request.batch_info, 'batch_number'):
            batch_number = request.batch_info.batch_number
        
        if not batch_number:
            batch_number = self._generate_batch_number(request.product_id, request.warehouse_id)

        # Create batch data
        batch_data = {
            "batch_number": batch_number,
            "product_id": request.product_id,
            "warehouse_id": request.warehouse_id,
            "quantity": request.amount,
            "available_quantity": request.amount,
            "reserved_quantity": 0.0,
            "created_by": created_by
        }

        # Add batch-specific information if provided
        if hasattr(request, 'batch_info') and request.batch_info:
            if hasattr(request.batch_info, 'cost_price') and request.batch_info.cost_price:
                batch_data["cost_price"] = request.batch_info.cost_price
            if hasattr(request.batch_info, 'selling_price') and request.batch_info.selling_price:
                batch_data["selling_price"] = request.batch_info.selling_price
            if hasattr(request.batch_info, 'manufacture_date') and request.batch_info.manufacture_date:
                batch_data["manufacture_date"] = request.batch_info.manufacture_date
            if hasattr(request.batch_info, 'expiry_date') and request.batch_info.expiry_date:
                batch_data["expiry_date"] = request.batch_info.expiry_date
            if hasattr(request.batch_info, 'notes') and request.batch_info.notes:
                batch_data["notes"] = request.batch_info.notes

        # Create the batch
        created_batch = self.repository.create_batch(batch_data)

        # Add product to warehouse if not already added
        try:
            self.repository.add_product_to_warehouse(
                product_id=request.product_id,
                warehouse_id=request.warehouse_id,
                batch_id=created_batch.id,
                minimum_stock=0.0
            )
        except ValueError:
            # Relationship might already exist, continue
            pass

        # Create amount ledger transaction
        transaction_reference = getattr(request, 'transaction_reference', f"GRN-{batch_number}")
        notes = getattr(request, 'notes', f"Stock received - Batch: {batch_number}")
        
        self.repository.receive(
            product_id=request.product_id,
            amount=request.amount,
            warehouse_id=request.warehouse_id,
            batch_id=created_batch.id,
            created_by=created_by,
            transaction_reference=transaction_reference,
            notes=notes
        )

        updated_product = self.repository.get(request.product_id)
        return updated_product
        
    def deplete_product(self, request: GRNRequest, created_by: UUID, batch_id: Optional[UUID] = None) -> Product:
        """
        Deplete product from inventory - reduces stock from specific batch or FIFO
        """
        # Validate product exists
        product = self.get_product_by_id(request.product_id)
        if not product:
            raise ErrorFactory.not_found("Product")
        
        # Validate warehouse exists
        warehouse = self.warehouse_service.get_warehouse_by_id(request.warehouse_id)
        if not warehouse:
            raise ErrorFactory.not_found("Warehouse")

        # If no batch specified, use FIFO (First In, First Out)
        if not batch_id:
            available_batches = self.repository.get_batches_by_product(
                product_id=request.product_id,
                warehouse_id=request.warehouse_id
            )
            
            # Filter batches with available quantity and sort by received date
            available_batches = [
                batch for batch in available_batches 
                if batch.available_quantity > 0
            ]
            available_batches.sort(key=lambda x: x.received_date)
            
            if not available_batches:
                raise ErrorFactory.business_rule_violation("No available stock for depletion")
            
            batch_id = available_batches[0].id

        # Validate batch has sufficient stock
        batch = self.repository.get_batch(batch_id)
        if not batch:
            raise ErrorFactory.not_found("Batch")
        
        if batch.available_quantity < request.amount:
            raise ErrorFactory.business_rule_violation(
                f"Insufficient stock. Available: {batch.available_quantity}, Requested: {request.amount}"
            )

        # Create amount ledger transaction
        transaction_reference = getattr(request, 'transaction_reference', f"OUT-{batch.batch_number}")
        notes = getattr(request, 'notes', f"Stock depleted - Batch: {batch.batch_number}")
        
        updated_product = self.repository.deplete(
            product_id=request.product_id,
            amount=request.amount,
            warehouse_id=request.warehouse_id,
            batch_id=batch_id,
            created_by=created_by,
            transaction_reference=transaction_reference,
            notes=notes
        )

        return Product.from_orm(updated_product)

    def get_product_batches(self, product_id: UUID, warehouse_id: Optional[UUID] = None) -> list:
        """Get all batches for a product"""
        self.get_product_by_id(product_id)
        batches = self.repository.get_batches_by_product(product_id, warehouse_id)
        
        return [
            {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "available_quantity": batch.available_quantity,
                "reserved_quantity": batch.reserved_quantity,
                "cost_price": batch.cost_price,
                "selling_price": batch.selling_price,
                "manufacture_date": batch.manufacture_date,
                "expiry_date": batch.expiry_date,
                "received_date": batch.received_date,
                "warehouse_id": batch.warehouse_id,
                "notes": batch.notes
            }
            for batch in batches
        ]

    def get_warehouse_stock(self, product_id: UUID, warehouse_id: UUID) -> dict:
        """Get warehouse stock summary for a product"""
        self.get_product_by_id(product_id)
        warehouse = self.warehouse_service.get_warehouse_by_id(warehouse_id)
        if not warehouse:
            raise ErrorFactory.not_found("Warehouse")

        batches = self.repository.get_batches_by_product(product_id, warehouse_id)
        
        total_quantity = sum(batch.quantity for batch in batches)
        total_available = sum(batch.available_quantity for batch in batches)
        total_reserved = sum(batch.reserved_quantity for batch in batches)

        return {
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "total_quantity": total_quantity,
            "available_quantity": total_available,
            "reserved_quantity": total_reserved,
            "batch_count": len(batches),
            "batches": [
                {
                    "id": batch.id,
                    "batch_number": batch.batch_number,
                    "available_quantity": batch.available_quantity,
                    "expiry_date": batch.expiry_date
                }
                for batch in batches
            ]
        }

    def get_all_categories(self) -> CategoryList:
        """Get all categories"""
        categories = self.repository.list_category()
        return CategoryList(categories=[Category.from_orm(c) for c in categories])

    def get_category_by_id(self, id: UUID) -> CategoryDetail:
        """Get category by ID"""
        category = self.repository.get_category(id)
        if not category:
            raise ErrorFactory.not_found("Category")
        return CategoryDetail.from_orm(category)

    def create_category(self, category: CategoryCreate, created_by: UUID) -> Category:
        """Create a new category"""
        category_dict = {
            "name": category.name,
            "description": category.description,
            "created_by": created_by
        }
        if hasattr(category, 'image'):
            category_dict["image"] = category.image
            
        saved_category = self.repository.create_category(category_dict)
        return Category.from_orm(saved_category)

    def update_category(self, category: CategoryUpdate, modified_by: UUID) -> CategoryDetail:
        """Update an existing category"""
        existing_category = self.get_category_by_id(category.id)
        if not existing_category:
            raise ErrorFactory.not_found("Category")
            
        category_dict = {
            "name": category.name,
            "description": category.description,
            "modified_by": modified_by
        }
        if hasattr(category, 'image'):
            category_dict["image"] = category.image
        
        saved_category = self.repository.update_category(category.id, category_dict)
        return CategoryDetail.from_orm(saved_category)

    def delete_category(self, category_id: UUID) -> None:
        """Delete a category"""
        existing_category = self.get_category_by_id(category_id)
        if not existing_category:
            raise ErrorFactory.not_found("Category")
        self.repository.delete_category(category_id)

    def search_categories(self, query: str) -> CategoryList:
        """Search categories"""
        categories = self.repository.search_categories(query)
        return CategoryList(categories=[Category.from_orm(c) for c in categories])

    def add_product_to_category(self, product_id: UUID, category_id: UUID) -> None:
        """Add product to category"""
        self.get_product_by_id(product_id)
        self.get_category_by_id(category_id)
        self.repository.add_product_to_category(product_id, category_id)

    def remove_product_from_category(self, product_id: UUID, category_id: UUID) -> None:
        """Remove product from category"""
        self.repository.remove_product_from_category(product_id, category_id)

    def get_products_by_category(self, category_id: UUID) -> ProductList:
        """Get all products in a category"""
        self.get_category_by_id(category_id)
        products = self.repository.get_products_by_category(category_id)
        return ProductList(products=[Product.from_orm(p) for p in products])

    def get_categories_by_product(self, product_id: UUID) -> CategoryList:
        """Get all categories for a product"""
        self.get_product_by_id(product_id)
        categories = self.repository.get_categories_by_product(product_id)
        return CategoryList(categories=[Category.from_orm(c) for c in categories])

    def update_product_crop_ratio(self, product_id: UUID, crop_id: UUID, quantity_ratio: float) -> None:
        """Update the quantity ratio for a product-crop relationship"""
        self.get_product_by_id(product_id)
        crop = self.crop_service.get_crop_by_id(crop_id)
        if not crop:
            raise ErrorFactory.not_found(f"Crop with ID {crop_id}")
        
        self.repository.update_product_crop_ratio(product_id, crop_id, quantity_ratio)