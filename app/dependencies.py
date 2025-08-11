from sqlalchemy.orm import Session
from typing import Annotated
from functools import lru_cache
from fastapi import Depends

from app.modules.authentication.service import AuthenticationService
from app.adapters.authentication.keycloak import KeycloakAdapter
from app.adapters.biodata.db import BiodataRepository
from app.adapters.employee.db import EmployeeRepository
from app.adapters.farmers.db import FarmerRepository
from app.adapters.product.db import ProductRepository
from app.adapters.resource.db import ResourceRepository
from app.adapters.role.db import RoleRepository
from app.adapters.warehouse.db import WarehouseRepository
from app.adapters.user.db import UserRepository

from app.config import settings
from app.modules.biodata.service import BiodataService
from app.modules.employees.service import EmployeeService
from app.modules.farmers.service import FarmerService
from app.modules.products.service import ProductService
from app.modules.resources.service import ResourceService
from app.modules.roles.service import RoleService
from app.modules.warehouse.service import WarehouseService
from app.modules.users.service import UserService

from app.database import get_db

@lru_cache()
def get_auth_adapter() -> KeycloakAdapter:
    """Get Keycloak adapter (singleton)"""
    return KeycloakAdapter(
        server_url=settings.KEYCLOAK_URL,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        client_secret=settings.KEYCLOAK_CLIENT_SECRET,
        realm=settings.KEYCLOAK_REALM,
    )

@lru_cache()
def get_auth_service(
    adapter: KeycloakAdapter = Depends(get_auth_adapter)
) -> AuthenticationService:
    """Get authentication service (singleton)"""
    return AuthenticationService(adapter)

def get_user_service(
    db: Session = Depends(get_db),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> UserService:
    return UserService(
        authentication_service=auth_service, 
        user_repository=UserRepository(db)
    )

def get_farmer_service(db: Session = Depends(get_db)) -> FarmerService:
    return FarmerService(farmer_repository=FarmerRepository(db))

def get_biodata_service(
    db: Session = Depends(get_db),
    farmer_service: FarmerService = Depends(get_farmer_service),
) -> BiodataService:
    return BiodataService(
        farmer_service=farmer_service, 
        biodata_repository=BiodataRepository(db)
    )

def get_resource_service(db: Session = Depends(get_db)) -> ResourceService:
    return ResourceService(resource_repository=ResourceRepository(db))

def get_role_service(
    db: Session = Depends(get_db),
    resource_service: ResourceService = Depends(get_resource_service),
) -> RoleService:
    return RoleService(
        role_repository=RoleRepository(db), 
        resource_service=resource_service
    )

def get_warehouse_service(
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
) -> WarehouseService:
    return WarehouseService(
        user_service=user_service, 
        warehouse_repository=WarehouseRepository(db)
    )

def get_product_service(
    db: Session = Depends(get_db),
    biodata_service: BiodataService = Depends(get_biodata_service),
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
) -> ProductService:
    return ProductService(
        product_repository=ProductRepository(db), 
        crop_service=biodata_service, 
        warehouse_service=warehouse_service
    )

def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    """Create EmployeeService with database session"""
    return EmployeeService(employee_repository=EmployeeRepository(db))


AuthServiceDep = Annotated[AuthenticationService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
FarmerServiceDep = Annotated[FarmerService, Depends(get_farmer_service)]
BiodataServiceDep = Annotated[BiodataService, Depends(get_biodata_service)]
ResourceServiceDep = Annotated[ResourceService, Depends(get_resource_service)]
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
WarehouseServiceDep = Annotated[WarehouseService, Depends(get_warehouse_service)]
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]