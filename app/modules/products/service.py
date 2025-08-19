from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from app.adapters.product.interface import IProductRepository
from app.core.exceptions import ErrorFactory
from app.modules.products.schemas import (
    ProductList, ProductCreate, Product, ProductDetail, ProductUpdate,
    GRNRequest, CategoryList, CategoryCreate, Category, CategoryDetail, CategoryUpdate
)
from app.modules.biodata.service import BiodataService
from app.modules.warehouse.service import WarehouseService
from app.logging import logger

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
        Deplete product from inventory - reduces reserved stock (for confirmed orders)
        Supports multi-batch depletion using FIFO
        """
        if request.amount <= 0:
            raise ErrorFactory.bad_request("Depletion amount must be positive")
        
        product = self._validate_product_and_warehouse(request.product_id, request.warehouse_id)
        
        if batch_id:
            batch = self.repository.get_batch(batch_id)
            if not batch:
                raise ErrorFactory.not_found("Batch")
            
            if float(batch.reserved_quantity) < request.amount:
                raise ErrorFactory.bad_request(
                    f"Insufficient reserved stock in batch. Reserved: {batch.reserved_quantity}, Requested: {request.amount}"
                )
            
            return self._deplete_from_single_batch(request, created_by, batch)
        else:
            available_batches = self._get_available_batches_for_depletion(
                request.product_id, 
                request.warehouse_id
            )
            
            if not available_batches:
                raise ErrorFactory.bad_request("No reserved stock available for depletion")
            
            total_reserved = sum(float(batch.reserved_quantity) for batch in available_batches)
            if total_reserved < request.amount:
                raise ErrorFactory.bad_request(
                    f"Insufficient reserved stock. Reserved: {total_reserved}, Requested: {request.amount}"
                )
            
            return self._deplete_from_multiple_batches(request, created_by, available_batches)

    def reserve_product(self, product_id: UUID, amount: float, created_by: UUID, 
                       warehouse_id: Optional[UUID] = None) -> Product:

        if amount <= 0:
            raise ErrorFactory.bad_request("Reservation amount must be positive")
        
        product = self._validate_product_and_warehouse(product_id, warehouse_id)
        
        available_batches = self._get_available_batches_for_reservation(product_id, warehouse_id)
        
        if not available_batches:
            raise ErrorFactory.bad_request("Product out of stock")
        
        total_available = sum(float(batch.available_quantity) for batch in available_batches)
        if total_available < amount:
            raise ErrorFactory.bad_request(
                f"Insufficient stock. Available: {total_available}, Requested: {amount}"
            )
        
        remaining_to_reserve = amount
        reservations_made = []
        
        for batch in available_batches:
            if remaining_to_reserve <= 0:
                break
            
            available_in_batch = batch.available_quantity
            reserve_from_batch = min(available_in_batch, remaining_to_reserve)
            
            new_available = available_in_batch - reserve_from_batch
            new_reserved = batch.reserved_quantity + reserve_from_batch
            
            self.repository.update_batch_quantities(
                batch_id=batch.id,
                available_qty=new_available,
                reserved_qty=new_reserved
            )
            
            self.repository.create_amount_transaction({
                'transaction_type': 'PURCHASE',
                'quantity_change': -reserve_from_batch,
                'product_id': product_id,
                'warehouse_id': batch.warehouse_id,
                'batch_id': batch.id,
                'created_by': created_by,
                'transaction_reference': f"RSV-{batch.batch_number}",
                'notes': f"Reserved for order - Batch: {batch.batch_number}",
                'reason': 'Stock reservation'
            })
            
            reservations_made.append({
                'batch_id': batch.id,
                'amount': reserve_from_batch
            })
            
            remaining_to_reserve -= reserve_from_batch
        
        logger.info(f"Reserved {amount} units of product {product_id} across {len(reservations_made)} batches")
        return self.repository.get(product_id)

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



    def _validate_product_and_warehouse(self, product_id: UUID, warehouse_id: Optional[UUID] = None):
        """Centralized validation for product and warehouse existence"""
        product = self.get_product_by_id(product_id)
        if not product:
            raise ErrorFactory.not_found("Product")
        
        if warehouse_id:
            warehouse = self.warehouse_service.get_warehouse_by_id(warehouse_id)
            if not warehouse:
                raise ErrorFactory.not_found("Warehouse")
        
        return product

    def _get_available_batches_for_reservation(self, product_id: UUID, warehouse_id: Optional[UUID] = None) -> List:
        """Get batches with available quantity for reservation"""
        batches = self.repository.get_batches_by_product(
            product_id=product_id,
            warehouse_id=warehouse_id
        )
        
        available_batches = [
            batch for batch in batches 
            if batch.available_quantity > 0
        ]
        
        available_batches.sort(key=lambda x: x.received_date)
        return available_batches

    def _get_available_batches_for_depletion(self, product_id: UUID, warehouse_id: UUID) -> List:
        """Get batches with reserved quantity for depletion"""
        batches = self.repository.get_batches_by_product(
            product_id=product_id,
            warehouse_id=warehouse_id
        )
        
        available_batches = [
            batch for batch in batches 
            if batch.reserved_quantity > 0
        ]
        
        available_batches.sort(key=lambda x: x.received_date)
        return available_batches

    def _deplete_from_single_batch(self, request: GRNRequest, created_by: UUID, batch) -> Product:
        """Deplete from a specific batch"""
        new_reserved = float(batch.reserved_quantity) - request.amount
        
        self.repository.update_batch_quantities(
            batch_id=batch.id,
            available_qty=float(batch.available_quantity),
            reserved_qty=new_reserved
        )
        
        transaction_reference = getattr(request, 'transaction_reference', f"OUT-{batch.batch_number}")
        notes = getattr(request, 'notes', f"Stock depleted - Batch: {batch.batch_number}")
        
        self.repository.create_amount_transaction({
            'transaction_type': 'SALE',
            'quantity_change': -request.amount,
            'product_id': request.product_id,
            'warehouse_id': request.warehouse_id,
            'batch_id': batch.id,
            'created_by': created_by,
            'transaction_reference': transaction_reference,
            'notes': notes,
            'reason': 'Stock depleted'
        })
        
        return self.repository.get(request.product_id)

    def _deplete_from_multiple_batches(self, request: GRNRequest, created_by: UUID, batches: List) -> Product:
        """Deplete across multiple batches using FIFO"""
        remaining_to_deplete = request.amount
        depletions_made = []
        
        for batch in batches:
            if remaining_to_deplete <= 0:
                break
            
            reserved_in_batch = float(batch.reserved_quantity)
            deplete_from_batch = min(reserved_in_batch, remaining_to_deplete)
            
            # Update batch quantities
            new_reserved = reserved_in_batch - deplete_from_batch
            self.repository.update_batch_quantities(
                batch_id=batch.id,
                available_qty=float(batch.available_quantity),
                reserved_qty=new_reserved
            )
            
            # Create transaction record
            transaction_reference = f"OUT-{batch.batch_number}"
            notes = f"Partial depletion - Batch: {batch.batch_number}"
            
            self.repository.create_amount_transaction({
                'transaction_type': 'SALE',
                'quantity_change': -deplete_from_batch,
                'product_id': request.product_id,
                'warehouse_id': request.warehouse_id,
                'batch_id': batch.id,
                'created_by': created_by,
                'transaction_reference': transaction_reference,
                'notes': notes,
                'reason': 'Stock depleted'
            })
            
            depletions_made.append({
                'batch_id': batch.id,
                'amount': deplete_from_batch
            })
            
            remaining_to_deplete -= deplete_from_batch
        
        logger.info(f"Depleted {request.amount} units of product {request.product_id} across {len(depletions_made)} batches")
        return self.repository.get(request.product_id)

    def unreserve_product(self, product_id: UUID, amount: float, created_by: UUID, 
                         warehouse_id: Optional[UUID] = None, order_id: Optional[UUID] = None) -> Product:
        """
        Unreserve product (for cancellations/returns) - moves reserved back to available
        """

        if amount <= 0:
            raise ErrorFactory.bad_request("Unreservation amount must be positive")
        
        product = self._validate_product_and_warehouse(product_id, warehouse_id)
        
        available_batches = self._get_available_batches_for_depletion(product_id, warehouse_id)
        
        if not available_batches:
            raise ErrorFactory.bad_request("No reserved stock to unreserve")
        
        total_reserved = sum(float(batch.reserved_quantity) for batch in available_batches)
        if total_reserved < amount:
            raise ErrorFactory.bad_request(
                f"Insufficient reserved stock to unreserve. Reserved: {total_reserved}, Requested: {amount}"
            )
        
        remaining_to_unreserve = amount
        unreservations_made = []
        
        for batch in available_batches:
            if remaining_to_unreserve <= 0:
                break
            
            reserved_in_batch = batch.reserved_quantity
            unreserve_from_batch = min(reserved_in_batch, remaining_to_unreserve)
            
            new_available = batch.available_quantity + unreserve_from_batch
            print(new_available, "New Available")
            new_reserved = reserved_in_batch - unreserve_from_batch
            
            self.repository.update_batch_quantities(
                batch_id=batch.id,
                available_qty=new_available,
                reserved_qty=new_reserved
            )
            
            transaction_reference = f"UNRSV-{batch.batch_number}"
            if order_id:
                transaction_reference += f"-{str(order_id)[:8]}"
            
            notes = f"Stock unreserved - Batch: {batch.batch_number}"
            if order_id:
                notes += f" (Order: {order_id})"
            
            self.repository.create_amount_transaction({
                'transaction_type': 'RETURN',
                'quantity_change': unreserve_from_batch,
                'product_id': product_id,
                'warehouse_id': batch.warehouse_id,
                'batch_id': batch.id,
                'created_by': created_by,
                'transaction_reference': transaction_reference,
                'notes': notes,
                'reason': 'Stock unreservation'
            })
            
            unreservations_made.append({
                'batch_id': batch.id,
                'amount': unreserve_from_batch
            })
            
            remaining_to_unreserve -= unreserve_from_batch
        
        logger.info(f"Unreserved {amount} units of product {product_id} across {len(unreservations_made)} batches")
        return self.repository.get(product_id)

    def get_product_availability(self, product_id: UUID, warehouse_id: Optional[UUID] = None) -> dict:
        """Get comprehensive availability information for a product"""
        product = self._validate_product_and_warehouse(product_id, warehouse_id)
        
        batches = self.repository.get_batches_by_product(product_id, warehouse_id)
        
        total_quantity = sum(float(batch.quantity) for batch in batches)
        total_available = sum(float(batch.available_quantity) for batch in batches)
        total_reserved = sum(float(batch.reserved_quantity) for batch in batches)
        
        return {
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "total_quantity": total_quantity,
            "available_quantity": total_available,
            "reserved_quantity": total_reserved,
            "can_reserve": total_available > 0,
            "can_deplete": total_reserved > 0,
            "batch_count": len(batches),
            "batches": [
                {
                    "id": batch.id,
                    "batch_number": batch.batch_number,
                    "total_quantity": float(batch.quantity),
                    "available_quantity": float(batch.available_quantity),
                    "reserved_quantity": float(batch.reserved_quantity),
                    "expiry_date": batch.expiry_date,
                    "received_date": batch.received_date
                }
                for batch in batches
            ]
        }