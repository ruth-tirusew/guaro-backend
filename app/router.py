from fastapi import APIRouter

from app.modules.authentication.router import router as authentication_router
from app.modules.employees.router import router as employee_router
from app.modules.farmers.router import router as farmer_router
from app.modules.biodata.router import router as biodata_router
from app.modules.order.router import router as order_router
from app.modules.products.router import router as product_router
from app.modules.products.router import category_router
from app.modules.resources.router import router as resource_router
from app.modules.roles.router import router as role_router
from app.modules.warehouse.router import router as warehouse_router
from app.modules.users.router import router as user_router
from app.modules.tax_and_charge.router import router as tax_router


prefix ="/api/v1"

routers = APIRouter()

routers.include_router(authentication_router, prefix=prefix)
routers.include_router(biodata_router, prefix=prefix)
routers.include_router(employee_router, prefix=prefix)
routers.include_router(farmer_router, prefix=prefix)
routers.include_router(order_router, prefix=prefix)
routers.include_router(product_router, prefix=prefix)
routers.include_router(category_router, prefix=prefix)
routers.include_router(role_router, prefix=prefix)
routers.include_router(resource_router, prefix=prefix)
routers.include_router(user_router, prefix=prefix)
routers.include_router(warehouse_router, prefix=prefix)
routers.include_router(tax_router, prefix=prefix)





