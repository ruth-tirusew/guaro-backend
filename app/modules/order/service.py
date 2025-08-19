import io
import csv
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal

from app.adapters.order.interface import IOrderRepository
from app.core.exceptions import ErrorFactory
from app.logging import logger
from app.modules.products.service import ProductService
from app.modules.products.schemas import GRNRequest
from app.modules.order.schemas import (
    CustomerCreate,CustomerUpdate,CustomerResponse,CustomerList,CustomerWithOrders,CustomerFilter,
    OrderCreate,OrderUpdate,OrderResponse,OrderWithDetails,OrderSummary,OrderList,OrderSummaryList,
    OrderFilter,OrderStatusUpdate,BulkOrderStatusUpdate,OrderFinancialSummary,OrderItemCreate,
    OrderItemUpdate,OrderItemResponse,AddItemToOrder,UpdateOrderItem,OrderStatus
)


class OrderService:
    def __init__(self, order_repository: IOrderRepository, product_service: ProductService):
        self.repository = order_repository
        self.product_service = product_service

    def create_customer(self, customer_data: CustomerCreate) -> CustomerResponse:
        """Create a new customer"""
        try:
            customer_dict = customer_data.model_dump()
            created_customer = self.repository.create_customer(customer_dict)
            return CustomerResponse.model_validate(created_customer)
        except Exception as e:
            logger.error(f"Service error creating customer: {str(e)}")
            raise

    def get_customer_by_id(self, customer_id: UUID) -> CustomerResponse:
        """Get customer by ID"""
        customer = self.repository.get_customer_by_id(customer_id)
        if not customer:
            raise ErrorFactory.not_found(
                resource="Customer",
                user_message="Customer not found"
            )
        return CustomerResponse.model_validate(customer)

    def get_customer_by_phone(self, phone: str) -> Optional[CustomerResponse]:
        """Get customer by phone number"""
        customer = self.repository.get_customer_by_phone(phone)
        return CustomerResponse.model_validate(customer) if customer else None

    def get_customer_by_email(self, email: str) -> Optional[CustomerResponse]:
        """Get customer by email"""
        customer = self.repository.get_customer_by_email(email)
        return CustomerResponse.model_validate(customer) if customer else None

    def update_customer(self, customer_id: UUID, customer_data: CustomerUpdate) -> CustomerResponse:
        """Update customer information"""
        update_dict = {k: v for k, v in customer_data.model_dump().items() if v is not None}
        if not update_dict:
            raise ErrorFactory.bad_request(
                message="No valid fields to update"
            )
        
        updated_customer = self.repository.update_customer(customer_id, update_dict)
        if not updated_customer:
            raise ErrorFactory.not_found(
                resource="Customer",
                user_message="Customer not found"
            )
        return CustomerResponse.model_validate(updated_customer)

    def delete_customer(self, customer_id: UUID) -> None:
        """Delete customer"""
        if not self.repository.delete_customer(customer_id):
            raise ErrorFactory.not_found(
                resource="Customer",
                user_message="Customer not found"
            )

 
    def get_customer_with_orders(self, customer_id: UUID) -> CustomerWithOrders:
        """Get customer with their order history"""
        customer = self.repository.get_customer_by_id(customer_id)
        if not customer:
            raise ErrorFactory.not_found(
                resource="Customer",
                user_message="Customer not found"
            )
        
        orders = self.repository.get_orders_by_customer(customer_id)
        order_summaries = [
            OrderSummary(
                id=order.id,
                order_number=order.order_number,
                customer_name=f"{customer.first_name} {customer.last_name}",
                status=order.status,
                order_date=order.order_date,
                total_amount=order.total_amount,
                items_count=len(order.order_items) if order.order_items else 0
            ) for order in orders
        ]
        
        customer_response = CustomerResponse.model_validate(customer)
        return CustomerWithOrders(
            **customer_response.model_dump(),
            orders=order_summaries
        )

    # Order Service Methods
    def create_order(self, order_data: OrderCreate, created_by: UUID) -> OrderResponse:
        """Create a new order with items"""
        try:
            order_dict = order_data.model_dump(exclude={'items'})
            order_dict['created_by']=created_by
            if not order_dict.get('order_number'):
                order_dict['order_number'] = self._generate_order_number()
            
            created_order = self.repository.create_order(order_dict)
            
            if order_data.items:
                items_data = []
                for item in order_data.items:
                    self.product_service.reserve_product(item.product_id, item.quantity, created_by)
                    product = self.product_service.get_product_by_id(item.product_id)
                    if not product:
                        raise ErrorFactory.bad_request(
                            message="Product not fount"
                        )
                    item_dict = item.model_dump()
                    item_dict['product_name']=product.name
                    item_dict['product_sku']=product.sku
                    item_dict['unit_of_measure']=product.unit_of_measure
                    item_dict['order_id'] = created_order.id
                    items_data.append(item_dict)
                
                self.repository.bulk_add_order_items(created_order.id, items_data)
                
                self._recalculate_order_totals(created_order.id)
            
            # Refresh and return
            final_order = self.repository.get_order_by_id(created_order.id)
            return OrderResponse.model_validate(final_order)
            
        except Exception as e:
            logger.error(f"Service error creating order: {str(e)}")
            raise

    def get_order_by_id(self, order_id: UUID) -> OrderResponse:
        """Get order by ID"""
        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )
        return OrderResponse.model_validate(order)

    def get_order_with_details(self, order_id: UUID) -> OrderWithDetails:
        """Get order with full details including customer and items"""
        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )
        return OrderWithDetails.model_validate(order)

    def get_order_by_number(self, order_number: str) -> OrderResponse:
        """Get order by order number"""
        order = self.repository.get_order_by_number(order_number)
        if not order:
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )
        return OrderResponse.model_validate(order)

    def update_order(self, order_id: UUID, order_data: OrderUpdate) -> OrderResponse:
        """Update order information"""
        update_dict = {k: v for k, v in order_data.model_dump().items() if v is not None}
        if not update_dict:
            raise ErrorFactory.bad_request(
                message="No valid fields to update"
            )
        
        updated_order = self.repository.update_order(order_id, update_dict)
        if not updated_order:
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )
        return OrderResponse.model_validate(updated_order)

    def update_order_status(self, order_id: UUID, status_data: OrderStatusUpdate) -> OrderResponse:
        updated_order = self.repository.update_order_status(
            order_id=order_id,
            status=status_data.status,
            modified_by=status_data.modified_by
        )

        if not updated_order:
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )

        match status_data.status:
            case OrderStatus.CONFIRMED | OrderStatus.DELIVERED:
                for item in updated_order.order_items:
                    request = GRNRequest(
                        warehouse_id=updated_order.warehouse_id,
                        product_id=item.product_id,
                        amount=item.quantity
                    )
                    self.product_service.deplete_product(request, status_data.modified_by)


            case OrderStatus.CANCELLED | OrderStatus.RETURNED:
                # TODO: restock
                pass

            case _:
                logger.warning(f"Unhandled order status transition: {status_data.status}")


        if status_data.notes:
            self.repository.update_order(order_id, {"notes": status_data.notes})

        return OrderResponse.model_validate(updated_order)

    def delete_order(self, order_id: UUID) -> None:
        """Delete order"""
        if not self.repository.delete_order(order_id):
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )

    def list_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[OrderFilter] = None
    ) -> OrderList:
        """List orders with filtering and pagination"""
        filter_params = {}
        if filters:
            filter_params = filters.model_dump(exclude_none=True)
            
        orders = self.repository.list_orders(skip, limit, **filter_params)
        order_responses = [OrderResponse.model_validate(order) for order in orders]
        
        total = len(order_responses) 
        pages = (total + limit - 1) // limit
        
        return OrderList(
            items=order_responses
        )

    def get_order_summaries(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[OrderFilter] = None
    ) -> OrderSummaryList:
        orders = self.list_orders(skip, limit, filters)
        summaries = []
        
        for order in orders.items:
            customer = self.repository.get_customer_by_id(order.customer_id)
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
            
            items = self.repository.get_order_items(order.id)
            
            summary = OrderSummary(
                id=order.id,
                order_number=order.order_number,
                customer_name=customer_name,
                status=order.status,
                order_date=order.order_date,
                total_amount=order.total_amount,
                items_count=len(items)
            )
            summaries.append(summary)
        
        return OrderSummaryList(
            items=summaries,
            total=orders.total,
            page=orders.page,
            size=orders.size,
            pages=orders.pages
        )

    def bulk_update_order_status(self, bulk_data: BulkOrderStatusUpdate) -> List[OrderResponse]:
        """Bulk update order status"""
        updated_orders = self.repository.bulk_update_order_status(
            bulk_data.order_ids,
            bulk_data.status
        )
        return [OrderResponse.model_validate(order) for order in updated_orders]

    def add_item_to_order(self, order_id: UUID, item_data: AddItemToOrder) -> OrderItemResponse:
        """Add item to an existing order"""
        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )
        
        item_dict = item_data.model_dump()
        item_dict['order_id'] = order_id
        
        product = self.product_service.get_product_by_id(item_data.product_id)
        item_dict['product_name'] = product.name
        item_dict['product_sku'] = product.sku
        item_dict['unit_of_measure'] = product.unit_of_measure
        
        created_item = self.repository.add_order_item(item_dict)
        
        self._recalculate_order_totals(order_id)
        
        return OrderItemResponse.model_validate(created_item)

    def update_order_item(self, item_id: UUID, item_data: UpdateOrderItem) -> OrderItemResponse:
        """Update order item"""
        update_dict = {k: v for k, v in item_data.model_dump().items() if v is not None}
        if not update_dict:
            raise ErrorFactory.bad_request(
                message="No valid fields to update"
            )
        
        updated_item = self.repository.update_order_item(item_id, update_dict)
        if not updated_item:
            raise ErrorFactory.not_found(
                resource="OrderItem",
                user_message="Order item not found"
            )
        
        self._recalculate_order_totals(updated_item.order_id)
        
        return OrderItemResponse.model_validate(updated_item)

    def delete_order_item(self, item_id: UUID) -> None:
        """Delete order item"""
        item = self.repository.get_order_item_by_id(item_id)
        if not item:
            raise ErrorFactory.not_found(
                resource="OrderItem",
                user_message="Order item not found"
            )
        
        order_id = item.order_id
        
        if not self.repository.delete_order_item(item_id):
            raise ErrorFactory.not_found(
                resource="OrderItem",
                user_message="Order item not found"
            )
        
        self._recalculate_order_totals(order_id)

    def get_order_items(self, order_id: UUID) -> List[OrderItemResponse]:
        """Get all items for an order"""
        if not self.repository.get_order_by_id(order_id):
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )
        
        items = self.repository.get_order_items(order_id)
        return [OrderItemResponse.model_validate(item) for item in items]

    def bulk_add_items_to_order(
        self,
        order_id: UUID,
        items_data: List[OrderItemCreate]
    ) -> List[OrderItemResponse]:
        """Add multiple items to an order"""
        if not self.repository.get_order_by_id(order_id):
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )
        
        items_dict_list = [item.model_dump() for item in items_data]
        created_items = self.repository.bulk_add_order_items(order_id, items_dict_list)
        
        self._recalculate_order_totals(order_id)
        
        return [OrderItemResponse.model_validate(item) for item in created_items]

    def clear_order_items(self, order_id: UUID) -> None:
        """Remove all items from an order"""
        if not self.repository.get_order_by_id(order_id):
            raise ErrorFactory.not_found(
                resource="Order",
                user_message="Order not found"
            )
        
        self.repository.clear_order_items(order_id)
        
        self.repository.update_order(order_id, {
            'subtotal': Decimal('0.0'),
            'tax_amount': Decimal('0.0'),
            'total_amount': Decimal('0.0')
        })

    def get_orders_by_customer(self, customer_id: UUID) -> List[OrderResponse]:
        """Get all orders for a customer"""
        orders = self.repository.get_orders_by_customer(customer_id)
        return [OrderResponse.model_validate(order) for order in orders]

    def get_orders_by_warehouse(self, warehouse_id: UUID) -> List[OrderResponse]:
        """Get all orders for a warehouse"""
        orders = self.repository.get_orders_by_warehouse(warehouse_id)
        return [OrderResponse.model_validate(order) for order in orders]

    def get_orders_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[OrderResponse]:
        """Get orders within a date range"""
        print(start_date)
        print(end_date)
        orders = self.repository.get_orders_by_date_range(start_date, end_date)
        print(orders)
        return orders

    def get_pending_orders(self) -> List[OrderResponse]:
        """Get all pending orders"""
        orders = self.repository.list_orders(status=OrderStatus.PENDING)
        return [OrderResponse.model_validate(order) for order in orders]

    def _generate_order_number(self) -> str:
        """Generate a unique order number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = str(uuid4())[:8].upper()
        return f"ORD-{timestamp}-{random_suffix}"

    def _recalculate_order_totals(self, order_id: UUID) -> None:
        """Recalculate order totals based on items"""
        try:
            items = self.repository.get_order_items(order_id)
            
            subtotal = sum(
                (item.quantity * item.unit_price) for item in items
            )
            total_discount = sum(item.discount_amount or Decimal('0.0') for item in items)
            total_tax = sum(item.tax_amount or Decimal('0.0') for item in items)
            
            order = self.repository.get_order_by_id(order_id)
            adjustment = order.adjustment if order else Decimal('0.0')
            order_discount = order.discount if order else Decimal('0.0')
            
            final_total = subtotal - total_discount - order_discount + adjustment + total_tax
            
            self.repository.update_order(order_id, {
                'subtotal': subtotal,
                'tax_amount': total_tax,
                'total_amount': final_total
            })
            
        except Exception as e:
            logger.error(f"Error recalculating order totals for {order_id}: {str(e)}")
            raise

    def export_order(
        self,
        start_date: datetime,
        end_date: datetime
    )->bytes:

        orders = self.get_orders_by_date_range(start_date=start_date, end_date=end_date)
        print(orders)
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Order ID', 'Order Number', 'Customer Name', 'Customer Phone',
            'Order Date', 'Status', 'Subtotal', 'Discount', 'Adjustment',
            'Tax Amount', 'Total Amount', 'Items Count'
        ])
        
        for order in orders:
            customer_name = ''
            customer_phone = ''
            if order.customer:
                customer_name = order.customer.full_name
                customer_phone = order.customer.phone
            
            writer.writerow([
                str(order.id),
                order.order_number,
                customer_name,
                customer_phone,
                order.order_date.isoformat() if order.order_date else '',
                order.status.value if order.status else '',
                str(order.subtotal or 0),
                str(order.total_discount or 0),
                str(order.adjustment or 0),
                str(order.tax_amount or 0),
                str(order.total_amount or 0),
                len(order.order_items)
            ])
        
        return output.getvalue().encode('utf-8')


    def _validate_order_data(self, order_data: Dict[str, Any]) -> None:
        """Validate order data before creation/update"""
        if order_data.get('delivery_date'):
            if order_data['delivery_date'] < datetime.now():
                raise ErrorFactory.bad_request(
                    message="Delivery date cannot be in the past"
                )
        
        for field in ['subtotal', 'discount', 'adjustment', 'tax_amount', 'total_amount']:
            if field in order_data and order_data[field] < 0:
                raise ErrorFactory.bad_request(
                    message=f"{field} cannot be negative"
                )


    def get_customer_order_stats(self, customer_id: UUID) -> Dict[str, Any]:
        """Get order statistics for a customer"""
        orders = self.repository.get_orders_by_customer(customer_id)
        
        if not orders:
            return {
                "total_orders": 0,
                "total_spent": Decimal('0.0'),
                "average_order_value": Decimal('0.0'),
                "last_order_date": None
            }
        
        total_spent = sum(order.total_amount or Decimal('0.0') for order in orders)
        
        return {
            "total_orders": len(orders),
            "total_spent": total_spent,
            "average_order_value": total_spent / len(orders),
            "last_order_date": max(order.order_date for order in orders)
        }