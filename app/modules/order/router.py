from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Response
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.modules.order.schemas import (
    # Customer Schemas
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerWithOrders,
    CustomerFilter,
    # Order Schemas
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderWithDetails,
    OrderSummary,
    OrderList,
    OrderSummaryList,
    OrderFilter,
    OrderStatusUpdate,
    BulkOrderStatusUpdate,
    OrderStatus,
    # Order Item Schemas
    AddItemToOrder,
    UpdateOrderItem,
    OrderItemResponse,

)
from app.adapters.order.interface import IOrderRepository
from app.core.exceptions import ErrorFactory
from app.dependencies import OrderServiceDep
from app.logging import logger
from app.modules.products.service import ProductService
from app.modules.order.service import OrderService
from app.utils.middlewares.authorization import require_auth

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)

@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    service: OrderServiceDep
):
    return service.create_customer(customer_data)


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id(
    customer_id: UUID,
    service: OrderServiceDep
):
    return service.get_customer_by_id(customer_id)

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: UUID,
    customer_data: CustomerUpdate,
    service: OrderServiceDep
):
    return service.update_customer(customer_id, customer_data)

@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: UUID,
    service: OrderServiceDep
):
    service.delete_customer(customer_id)

@router.get("/customers/{customer_id}/orders", response_model=CustomerWithOrders)
def get_customer_with_orders(
    customer_id: UUID,
    service: OrderServiceDep
):
    return service.get_customer_with_orders(customer_id)


@router.get("/customers/{customer_id}/stats")
def get_customer_order_stats(
    customer_id: UUID,
    service: OrderServiceDep
):
    return service.get_customer_order_stats(customer_id)


# ==============================================================================
# Order Endpoints
# ==============================================================================

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    service: OrderServiceDep,
    user_info: dict = Depends(require_auth()),

):
    print(user_info)
    return service.create_order(order_data, user_info.id)


# @router.get("/{order_id}", response_model=OrderResponse)
# def get_order_by_id(
#     order_id: UUID,
#     service: OrderServiceDep
# ):
#     return service.get_order_by_id(order_id)


@router.get("/{order_id}/details", response_model=OrderWithDetails)
def get_order_with_details(
    order_id: UUID,
    service: OrderServiceDep
):
    return service.get_order_with_details(order_id)


@router.get("/number/{order_number}", response_model=OrderResponse)
def get_order_by_number(
    order_number: str,
    service: OrderServiceDep
):
    return service.get_order_by_number(order_number)


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: UUID,
    order_data: OrderUpdate,
    service: OrderServiceDep
):
    return service.update_order(order_id, order_data)

@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: UUID,
    status: OrderStatus,
    service: OrderServiceDep,
    notes: Optional[str]=None,
    user_info: dict = Depends(require_auth()),

):
    request = OrderStatusUpdate(
        status=status,
        modified_by=user_info.id,
        notes=notes
    )
    return service.update_order_status(order_id, request)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: UUID,
    service: OrderServiceDep
):
    service.delete_order(order_id)


# ==============================================================================
# Order List & Filtering
# ==============================================================================

@router.get("/", response_model=OrderList)
def list_orders(
    service: OrderServiceDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=1000),
    filters: Optional[OrderFilter] = None,
):
    return service.list_orders(skip=skip, limit=limit, filters=filters)


@router.get("/summaries", response_model=OrderSummaryList)
def get_order_summaries(
    service: OrderServiceDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=1000),
    filters: Optional[OrderFilter] = None,
):
    return service.get_order_summaries(skip=skip, limit=limit, filters=filters)


@router.post("/bulk-status", response_model=List[OrderResponse])
def bulk_update_order_status(
    bulk_data: BulkOrderStatusUpdate,
    service: OrderServiceDep
):
    return service.bulk_update_order_status(bulk_data)


# ==============================================================================
# Order Items Endpoints
# ==============================================================================

@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_order(
    order_id: UUID,
    item_data: AddItemToOrder,
    service: OrderServiceDep
):
    try:
        return service.add_item_to_order(order_id, item_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/items/{item_id}", response_model=OrderItemResponse)
def update_order_item(
    item_id: UUID,
    item_data: UpdateOrderItem,
    service: OrderServiceDep
):
    return service.update_order_item(item_id, item_data)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(
    item_id: UUID,
    service: OrderServiceDep
):
    service.delete_order_item(item_id)

@router.get("/{order_id}/items", response_model=List[OrderItemResponse])
def get_order_items(
    order_id: UUID,
    service: OrderServiceDep
):
    return service.get_order_items(order_id)


@router.post("/{order_id}/items/bulk", response_model=List[OrderItemResponse])
def bulk_add_items_to_order(
    order_id: UUID,
    items_data: List[AddItemToOrder],
    service: OrderServiceDep
):
    return service.bulk_add_items_to_order(order_id, items_data)


# ==============================================================================
# Export Orders
# ==============================================================================

@router.get("/export")
def export_orders(
    start_date: datetime,
    end_date: datetime,
    service: OrderServiceDep
):
    try:
        data = service.export_order(start_date=start_date, end_date=end_date)
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"orders_export_{date_str}.csv"
        return Response(
            content=data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise ErrorFactory.internal_server_error(user_message="Export failed")