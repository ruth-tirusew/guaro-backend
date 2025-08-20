from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, List
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

# Customer Schemas
class CustomerBase(BaseModel):
    first_name: str = Field(..., max_length=255, description="Customer first name")
    last_name: str = Field(..., max_length=255, description="Customer last name")
    phone: Optional[str] = Field(None, max_length=20, description="Customer phone number")
    email: Optional[str] = Field(None, max_length=255, description="Customer email address")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)

class CustomerResponse(CustomerBase):
    id: UUID = Field(..., description="Customer ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name property"""
        return f"{self.first_name} {self.last_name}"
    
    model_config = ConfigDict(from_attributes=True)

# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: UUID = Field(..., description="Product ID")
    quantity: Decimal = Field(..., gt=0, description="Quantity ordered")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    discount_amount: Decimal = Field(default=Decimal('0.0'), ge=0, description="Discount amount")
    tax_amount: Decimal = Field(default=Decimal('0.0'), ge=0, description="Tax amount")
    notes: Optional[str] = Field(None, description="Item notes")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

class OrderItemResponse(OrderItemBase):
    id: UUID = Field(..., description="Order item ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @computed_field
    @property
    def line_total(self) -> Decimal:
        """Calculate line total: (quantity * unit_price) - discount + tax"""
        return (self.quantity * self.unit_price) - self.discount_amount + self.tax_amount
    
    @computed_field
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal before discount and tax"""
        return self.quantity * self.unit_price
    
    model_config = ConfigDict(from_attributes=True)

# Order Schemas
class OrderBase(BaseModel):
    customer_id: Optional[UUID] = None
    warehouse_id: UUID = Field(..., description="Warehouse ID")
    order_number: str = Field(..., max_length=100, description="Unique order number")
    order_date: datetime = Field(default_factory=lambda: datetime.now(), description="Order date")
    delivery_date: Optional[datetime] = Field(None, description="Expected delivery date")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    subtotal: Decimal = Field(default=Decimal('0.0'), ge=0, description="Subtotal amount")
    discount: Decimal = Field(default=Decimal('0.0'), ge=0, description="Discount amount")
    adjustment: Decimal = Field(default=Decimal('0.0'), description="Adjustment amount")
    tax_amount: Decimal = Field(default=Decimal('0.0'), ge=0, description="Tax amount")
    total_amount: Decimal = Field(default=Decimal('0.0'), ge=0, description="Total amount")
    notes: Optional[str] = Field(None, description="Order notes")
    created_by: UUID = Field(..., description="User who created the order")
    modified_by: Optional[UUID] = Field(None, description="User who last modified the order")

class OrderCreate(BaseModel):
    customer_id: Optional[UUID] = None    
    warehouse_id: UUID
    order_number: Optional[str] = Field(None, description="Auto-generated if not provided")
    delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate] = Field(default=[], description="Order items")

class OrderUpdate(BaseModel):
    warehouse_id: Optional[UUID] = None
    delivery_date: Optional[datetime] = None
    status: Optional[OrderStatus] = None
    discount: Optional[Decimal] = Field(None, ge=0)
    adjustment: Optional[Decimal] = None
    notes: Optional[str] = None
    modified_by: UUID  

class OrderResponse(OrderBase):
    id: UUID = Field(..., description="Order ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @computed_field
    @property
    def calculated_total(self) -> Decimal:
        """Calculate total from subtotal, discount, adjustment, and tax"""
        return self.subtotal - self.discount + self.adjustment + self.tax_amount
    
    model_config = ConfigDict(from_attributes=True)

class OrderWithDetails(OrderResponse):
    customer: Optional[CustomerResponse] = Field(None, description="Customer details")
    order_items: List[OrderItemResponse] = Field(default=[], description="Order items")
    # creator: Optional['UserResponse'] = Field(None, description="User who created the order")
    # modifier: Optional['UserResponse'] = Field(None, description="User who last modified the order")
    
    @computed_field
    @property
    def items_count(self) -> int:
        """Count of order items"""
        return len(self.order_items)

class OrderSummary(BaseModel):
    id: UUID
    order_number: str
    customer_name: str
    status: OrderStatus
    order_date: datetime
    total_amount: Decimal
    items_count: int
    
    model_config = ConfigDict(from_attributes=True)

class OrderList(BaseModel):
    items: List[OrderResponse]

class OrderSummaryList(BaseModel):
    items: List[OrderSummary]
    total: int
    page: int
    size: int
    pages: int

class OrderFilter(BaseModel):
    customer_id: Optional[UUID] = Field(None, description="Filter by customer")
    warehouse_id: Optional[UUID] = Field(None, description="Filter by warehouse")
    status: Optional[OrderStatus] = Field(None, description="Filter by status")
    order_number: Optional[str] = Field(None, description="Filter by order number")
    date_from: Optional[datetime] = Field(None, description="Filter orders from this date")
    date_to: Optional[datetime] = Field(None, description="Filter orders until this date")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum order amount")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum order amount")

class CustomerFilter(BaseModel):
    name: Optional[str] = Field(None, description="Filter by customer name")
    email: Optional[str] = Field(None, description="Filter by email")
    phone: Optional[str] = Field(None, description="Filter by phone")

# Bulk operations
class BulkOrderStatusUpdate(BaseModel):
    order_ids: List[UUID] = Field(..., min_length=1, description="List of order IDs")
    status: OrderStatus = Field(..., description="New status")
    modified_by: UUID  

class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(..., description="New order status")
    modified_by: UUID  
    notes: Optional[str] = Field(None, description="Status change notes")

class OrderFinancialSummary(BaseModel):
    total_orders: int
    total_revenue: Decimal
    total_tax: Decimal
    total_discount: Decimal
    average_order_value: Decimal
    
class CustomerOrderStats(BaseModel):
    customer_id: UUID
    customer_name: str
    total_orders: int
    total_spent: Decimal
    average_order_value: Decimal
    last_order_date: Optional[datetime]

class OrderItemWithProduct(OrderItemResponse):
    product: Optional['ProductResponse'] = Field(None, description="Product details")
    batch: Optional['ProductBatchResponse'] = Field(None, description="Batch details")

class AddItemToOrder(BaseModel):
    product_id: UUID
    batch_id: Optional[UUID] = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Optional[Decimal] = Field(None, description="Override product price if provided")
    notes: Optional[str] = None

class UpdateOrderItem(BaseModel):
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

class CustomerList(BaseModel):
    items: List[CustomerResponse]
    total: int
    page: int
    size: int
    pages: int

class CustomerWithOrders(CustomerResponse):
    orders: List[OrderSummary] = Field(default=[], description="Customer orders")
    
    @computed_field
    @property
    def total_orders(self) -> int:
        """Total number of orders"""
        return len(self.orders)
    
    @computed_field
    @property
    def total_spent(self) -> Decimal:
        """Total amount spent by customer"""
        return sum(order.total_amount for order in self.orders)