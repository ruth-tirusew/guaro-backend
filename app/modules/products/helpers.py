class InventoryValidator:
    @staticmethod
    def validate_batch_consistency(batch):
        """Validate that batch quantities are consistent"""
        total_accounted = float(batch.available_quantity) + float(batch.reserved_quantity)
        total_in_warehouse = float(batch.quantity)
        
        if abs(total_accounted - total_in_warehouse) > 0.01:  # Allow small floating point differences
            raise ValueError(
                f"Batch {batch.batch_number} quantities inconsistent. "
                f"Available + Reserved: {total_accounted}, Total: {total_in_warehouse}"
            )
        
        if any(float(qty) < 0 for qty in [batch.available_quantity, batch.reserved_quantity, batch.quantity]):
            raise ValueError(f"Batch {batch.batch_number} has negative quantities")
    
    @staticmethod
    def validate_inventory_operation(operation_type: str, batch, amount: float):
        """Validate inventory operations before execution"""
        if amount <= 0:
            raise ValueError(f"{operation_type} amount must be positive")
        
        if operation_type == "RESERVE":
            if float(batch.available_quantity) < amount:
                raise ErrorFactory.bad_request(
                    f"Insufficient available stock for reservation. Available: {batch.available_quantity}, Requested: {amount}"
                )
        
        elif operation_type == "DEPLETE":
            if float(batch.reserved_quantity) < amount:
                raise ErrorFactory.bad_request(
                    f"Insufficient reserved stock for depletion. Reserved: {batch.reserved_quantity}, Requested: {amount}"
                )
        
        elif operation_type == "UNRESERVE":
            if float(batch.reserved_quantity) < amount:
                raise ErrorFactory.bad_request(
                    f"Insufficient reserved stock for unreservation. Reserved: {batch.reserved_quantity}, Requested: {amount}"
                )