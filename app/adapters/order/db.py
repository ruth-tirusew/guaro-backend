import io
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.adapters.order.models import (
    Orders as Order,
    OrderItems,
    Customer,
    OrderStatus,
)
from app.adapters.order.interface import IOrderRepository
from app.core.exceptions import ErrorFactory
from app.logging import logger


class OrderRepository(IOrderRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    # Customer Operations
    def create_customer(self, customer_info: dict) -> Customer:
        """Create a new customer"""
        try:
            customer = Customer(**customer_info)
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)
            logger.info(f"Customer created: {customer.id}")
            return customer
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error creating customer: {str(e)}")
            raise ErrorFactory.conflict(
                resource="Customer",
                user_message="Customer with this phone or email already exists",
                context=customer_info
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating customer: {str(e)}")
            raise

    def get_customer_by_id(self, customer_id: UUID) -> Optional[Customer]:
        """Get customer by ID"""
        try:
            return self.db.query(Customer).filter(Customer.id == customer_id).first()
        except Exception as e:
            logger.error(f"Error getting customer by ID {customer_id}: {str(e)}")
            raise

    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone number"""
        try:
            return self.db.query(Customer).filter(Customer.phone == phone).first()
        except Exception as e:
            logger.error(f"Error getting customer by phone {phone}: {str(e)}")
            raise

    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        try:
            return self.db.query(Customer).filter(Customer.email == email).first()
        except Exception as e:
            logger.error(f"Error getting customer by email {email}: {str(e)}")
            raise

    def update_customer(self, customer_id: UUID, customer_info: dict) -> Optional[Customer]:
        """Update customer information"""
        try:
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                return None
            
            for key, value in customer_info.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            
            self.db.commit()
            self.db.refresh(customer)
            logger.info(f"Customer updated: {customer_id}")
            return customer
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error updating customer {customer_id}: {str(e)}")
            raise ErrorFactory.conflict(
                resource="Customer",
                user_message="Customer with this phone or email already exists",
                context={"customer_id": str(customer_id)}
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error updating customer {customer_id}: {str(e)}")
            raise

    def delete_customer(self, customer_id: UUID) -> bool:
        """Delete customer"""
        try:
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                return False
            
            self.db.delete(customer)
            self.db.commit()
            logger.info(f"Customer deleted: {customer_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting customer {customer_id}: {str(e)}")
            raise

    def list_customers(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Customer]:
        """List customers with pagination and optional search"""
        try:
            query = self.db.query(Customer)
            
            if search:
                search_filter = or_(
                    Customer.first_name.ilike(f"%{search}%"),
                    Customer.last_name.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error listing customers: {str(e)}")
            raise

    # Order Operations
    def create_order(self, order_info: dict) -> Order:
        """Create a new order"""
        try:
            order = Order(**order_info)
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            logger.info(f"Order created: {order.id}")
            return order
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error creating order: {str(e)}")
            raise ErrorFactory.conflict(
                resource="Order",
                user_message="Order with this number already exists",
                context=order_info
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating order: {str(e)}")
            raise

    def get_order_by_id(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        try:
            return self.db.query(Order).options(
                joinedload(Order.customer),
                joinedload(Order.order_items)
            ).filter(Order.id == order_id).first()
        except Exception as e:
            logger.error(f"Error getting order by ID {order_id}: {str(e)}")
            raise

    def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        try:
            return self.db.query(Order).options(
                joinedload(Order.customer),
                joinedload(Order.order_items)
            ).filter(Order.order_number == order_number).first()
        except Exception as e:
            logger.error(f"Error getting order by number {order_number}: {str(e)}")
            raise

    def update_order(self, order_id: UUID, order_info: dict) -> Optional[Order]:
        """Update order information"""
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return None
            
            allowed_fields = {'customer_id', 'warehouse_id', 'status', 'notes',
                              'subtotal', 'discount', 'adjustment', 'tax_amount', 'total_amount'}
            for key, value in order_info.items():
                if key in allowed_fields and hasattr(order, key):
                    setattr(order, key, value)
            
            self.db.commit()
            self.db.refresh(order)
            logger.info(f"Order updated: {order_id}")
            return order
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating order {order_id}: {str(e)}")
            raise

    def update_order_status(self, order_id: UUID, status: OrderStatus, notes: str) -> Optional[Order]:
        """Update order status"""
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return None
            
            order.status = status
            order.notes = notes
            self.db.commit()
            self.db.refresh(order)
            logger.info(f"Order status updated: {order_id} -> {status}")
            return order
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating order status {order_id}: {str(e)}")
            raise

    def delete_order(self, order_id: UUID) -> bool:
        """Delete order"""
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return False
            
            self.db.delete(order)
            self.db.commit()
            logger.info(f"Order deleted: {order_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting order {order_id}: {str(e)}")
            raise

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
        try:
            query = self.db.query(Order).options(
                joinedload(Order.customer),
                joinedload(Order.order_items)
            )
            
            if customer_id:
                query = query.filter(Order.customer_id == customer_id)
            if warehouse_id:
                query = query.filter(Order.warehouse_id == warehouse_id)
            if status:
                query = query.filter(Order.status == status)
            if date_from:
                query = query.filter(Order.order_date >= date_from)
            if date_to:
                query = query.filter(Order.order_date <= date_to)
            
            return query.order_by(desc(Order.order_date)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            raise

    def get_orders_without_customer(self) -> List[Order]:
        """Get all orders without assigned customers"""
        try:
            return self.db.query(Order).filter(
                Order.customer_id.is_(None)
            ).order_by(desc(Order.order_date)).all()
        except Exception as e:
            logger.error(f"Error getting orders without customer: {str(e)}")
            raise

    def assign_customer_to_order(self, order_id: UUID, customer_id: UUID) -> Optional[Order]:
        """Assign a customer to an existing order"""
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return None
            
            # Verify customer exists
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                raise ErrorFactory.not_found(
                    resource="Customer",
                    user_message="Customer not found",
                    context={"customer_id": str(customer_id)}
                )
            
            order.customer_id = customer_id
            self.db.commit()
            self.db.refresh(order)
            logger.info(f"Customer {customer_id} assigned to order {order_id}")
            return order
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning customer to order {order_id}: {str(e)}")
            raise

    def get_orders_by_customer(self, customer_id: UUID) -> List[Order]:
        """Get all orders for a specific customer"""
        try:
            return self.db.query(Order).filter(
                Order.customer_id == customer_id
            ).order_by(desc(Order.order_date)).all()
        except Exception as e:
            logger.error(f"Error getting orders by customer {customer_id}: {str(e)}")
            raise

    def get_orders_by_warehouse(self, warehouse_id: UUID) -> List[Order]:
        """Get all orders for a specific warehouse"""
        try:
            return self.db.query(Order).filter(
                Order.warehouse_id == warehouse_id
            ).order_by(desc(Order.order_date)).all()
        except Exception as e:
            logger.error(f"Error getting orders by warehouse {warehouse_id}: {str(e)}")
            raise

    def get_orders_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Order]:
        """Get orders within a date range"""
        try:
            orders = self.db.query(Order).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            ).order_by(desc(Order.created_at)).all()
            return orders
        except Exception as e:
            logger.error(f"Error getting orders by date range: {str(e)}")
            raise

    # Order Items Operations
    def add_order_item(self, order_item_info: dict) -> OrderItems:
        """Add item to an order"""
        try:
            order_item = OrderItems(**order_item_info)
            self.db.add(order_item)
            self.db.commit()
            self.db.refresh(order_item)
            logger.info(f"Order item added: {order_item.id}")
            return order_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding order item: {str(e)}")
            raise

    def get_order_item_by_id(self, item_id: UUID) -> Optional[OrderItems]:
        """Get order item by ID"""
        try:
            return self.db.query(OrderItems).filter(OrderItems.id == item_id).first()
        except Exception as e:
            logger.error(f"Error getting order item by ID {item_id}: {str(e)}")
            raise

    def update_order_item(self, item_id: UUID, item_info: dict) -> Optional[OrderItems]:
        """Update order item"""
        try:
            order_item = self.get_order_item_by_id(item_id)
            if not order_item:
                return None
            
            for key, value in item_info.items():
                if hasattr(order_item, key):
                    setattr(order_item, key, value)
            
            self.db.commit()
            self.db.refresh(order_item)
            logger.info(f"Order item updated: {item_id}")
            return order_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating order item {item_id}: {str(e)}")
            raise

    def delete_order_item(self, item_id: UUID) -> bool:
        """Delete order item"""
        try:
            order_item = self.get_order_item_by_id(item_id)
            if not order_item:
                return False
            
            self.db.delete(order_item)
            self.db.commit()
            logger.info(f"Order item deleted: {item_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting order item {item_id}: {str(e)}")
            raise

    def get_order_items(self, order_id: UUID) -> List[OrderItems]:
        """Get all items for a specific order"""
        try:
            return self.db.query(OrderItems).filter(
                OrderItems.order_id == order_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting order items for order {order_id}: {str(e)}")
            raise

    def bulk_add_order_items(self, order_id: UUID, items_info: List[dict]) -> List[OrderItems]:
        """Add multiple items to an order"""
        try:
            order_items = []
            for item_info in items_info:
                item_info['order_id'] = order_id
                order_item = OrderItems(**item_info)
                order_items.append(order_item)
                self.db.add(order_item)
            
            self.db.commit()
            for item in order_items:
                self.db.refresh(item)
            
            logger.info(f"Bulk added {len(order_items)} items to order {order_id}")
            return order_items
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk adding order items: {str(e)}")
            raise

    def bulk_update_order_items(self, items_info: List[dict]) -> List[OrderItems]:
        """Update multiple order items"""
        try:
            updated_items = []
            allowed_fields = {'product_id', 'quantity', 'unit_price', 'discount', 'tax_rate'}
            for item_info in items_info:
                item_id = item_info.get('id')
                if not item_id:
                    logger.warning("Skipping item update: missing 'id' field")
                    continue
                order_item = self.get_order_item_by_id(item_id)
                if not order_item:
                    logger.warning(f"Skipping item update: order item not found for id={item_id}")
                    continue
                for key, value in item_info.items():
                    if key in allowed_fields and hasattr(order_item, key):
                        setattr(order_item, key, value)
                updated_items.append(order_item)
                
                self.db.commit()
                for item in updated_items:
                    self.db.refresh(item)
                
                logger.info(f"Bulk updated {len(updated_items)} order items")
                return updated_items
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk updating order items: {str(e)}")
            raise

    def clear_order_items(self, order_id: UUID) -> bool:
        """Remove all items from an order"""
        try:
            deleted_count = self.db.query(OrderItems).filter(
                OrderItems.order_id == order_id
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleared {deleted_count} items from order {order_id}")
            return deleted_count > 0
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error clearing order items for order {order_id}: {str(e)}")
            raise

    def rollback_transaction(self):
        """Rollback database transaction"""
        try:
            self.db.rollback()
        except Exception as e:
            logger.error(f"Error rolling back transaction: {str(e)}")
            raise

    def bulk_update_order_status(
        self, 
        order_ids: List[UUID], 
        status: OrderStatus
    ) -> List[Order]:
        """Bulk update order status"""
        try:
            orders = self.db.query(Order).filter(Order.id.in_(order_ids)).all()
            
            for order in orders:
                order.status = status
            
            self.db.commit()
            for order in orders:
                self.db.refresh(order)
            
            logger.info(f"Bulk updated status for {len(orders)} orders to {status}")
            return orders
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk updating order status: {str(e)}")
            raise