from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.adapters.order.models import (
    Order,
    OrderItems,
    Customer,
    OrderStatus,
)

class IOrderRepository(ABC):
    @abstractmethod
    def create_customer(self, customer_info: dict) -> Customer:
        """Create a new customer"""
        pass
    
    @abstractmethod
    def get_customer_by_id(self, customer_id: UUID) -> Optional[Customer]:
        """Get customer by ID"""
        pass
    
    @abstractmethod
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone number"""
        pass
    
    @abstractmethod
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        pass
    
    @abstractmethod
    def update_customer(self, customer_id: UUID, customer_info: dict) -> Optional[Customer]:
        """Update customer information"""
        pass
    
    @abstractmethod
    def delete_customer(self, customer_id: UUID) -> bool:
        """Delete customer"""
        pass
    
    @abstractmethod
    def list_customers(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Customer]:
        pass
    
    @abstractmethod
    def create_order(self, order_info: dict) -> Order:
        """Create a new order"""
        pass
    
    @abstractmethod
    def get_order_by_id(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        pass
    
    @abstractmethod
    def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        pass
    
    @abstractmethod
    def update_order(self, order_id: UUID, order_info: dict) -> Optional[Order]:
        """Update order information"""
        pass
    
    @abstractmethod
    def update_order_status(self, order_id: UUID, status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        pass
    
    @abstractmethod
    def delete_order(self, order_id: UUID) -> bool:
        """Delete order"""
        pass
    
    @abstractmethod
    def list_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[UUID] = None,
        warehouse_id: Optional[UUID] = None,
        status: Optional[OrderStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Order]:
        """List orders with filtering options"""
        pass
    
    @abstractmethod
    def get_orders_by_customer(self, customer_id: UUID) -> List[Order]:
        """Get all orders for a specific customer"""
        pass
    
    @abstractmethod
    def get_orders_by_warehouse(self, warehouse_id: UUID) -> List[Order]:
        """Get all orders for a specific warehouse"""
        pass
    
    @abstractmethod
    def get_orders_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Order]:
        """Get orders within a date range"""
        pass
    
    # Order Items Operations
    @abstractmethod
    def add_order_item(self, order_item_info: dict) -> OrderItems:
        """Add item to an order"""
        pass
    
    @abstractmethod
    def get_order_item_by_id(self, item_id: UUID) -> Optional[OrderItems]:
        """Get order item by ID"""
        pass
    
    @abstractmethod
    def update_order_item(self, item_id: UUID, item_info: dict) -> Optional[OrderItems]:
        """Update order item"""
        pass
    
    @abstractmethod
    def delete_order_item(self, item_id: UUID) -> bool:
        """Delete order item"""
        pass
    
    @abstractmethod
    def get_order_items(self, order_id: UUID) -> List[OrderItems]:
        """Get all items for a specific order"""
        pass
    
    @abstractmethod
    def bulk_add_order_items(self, order_id: UUID, items_info: List[dict]) -> List[OrderItems]:
        """Add multiple items to an order"""
        pass
    
    @abstractmethod
    def bulk_update_order_items(self, items_info: List[dict]) -> List[OrderItems]:
        """Update multiple order items"""
        pass
    
    @abstractmethod
    def clear_order_items(self, order_id: UUID) -> bool:
        """Remove all items from an order"""
        pass
      
    @abstractmethod
    def begin_transaction(self):
        """Begin database transaction"""
        pass
    
    @abstractmethod
    def commit_transaction(self):
        """Commit database transaction"""
        pass
    
    @abstractmethod
    def rollback_transaction(self):
        """Rollback database transaction"""
        pass
    
    @abstractmethod
    def bulk_update_order_status(
        self, 
        order_ids: List[UUID], 
        status: OrderStatus
    ) -> List[Order]:
        """Bulk update order status"""
        pass
    
    @abstractmethod
    def export_orders(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "csv"
    ) -> bytes:
        """Export orders data"""
        pass