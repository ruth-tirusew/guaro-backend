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
from app.adapters.tax_and_charge.db import TaxRepository
from app.adapters.warehouse.db import WarehouseRepository
from app.adapters.user.db import UserRepository

from app.config import settings
from app.modules.biodata.service import BiodataService
from app.modules.employees.service import EmployeeService
from app.modules.farmers.service import FarmerService
from app.modules.products.service import ProductService
from app.modules.resources.service import ResourceService
from app.modules.roles.service import RoleService
from app.modules.tax_and_charge.service import TaxService
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

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Get user repository with database session"""
    return UserRepository(db)

def get_farmer_repository(db: Session = Depends(get_db)) -> FarmerRepository:
    """Get farmer repository with database session"""
    return FarmerRepository(db)

def get_biodata_repository(db: Session = Depends(get_db)) -> BiodataRepository:
    """Get biodata repository with database session"""
    return BiodataRepository(db)

def get_resource_repository(db: Session = Depends(get_db)) -> ResourceRepository:
    """Get resource repository with database session"""
    return ResourceRepository(db)

def get_role_repository(db: Session = Depends(get_db)) -> RoleRepository:
    """Get role repository with database session"""
    return RoleRepository(db)

def get_warehouse_repository(db: Session = Depends(get_db)) -> WarehouseRepository:
    """Get warehouse repository with database session"""
    return WarehouseRepository(db)

def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    """Get product repository with database session"""
    return ProductRepository(db)

def get_employee_repository(db: Session = Depends(get_db)) -> EmployeeRepository:
    """Get employee repository with database session"""
    return EmployeeRepository(db)

def get_tax_repository(db: Session = Depends(get_db)) -> TaxRepository:
    return TaxRepository(db)


# Service Layer Dependencies (Request-scoped)
def get_resource_service(
    resource_repository: ResourceRepository = Depends(get_resource_repository)
) -> ResourceService:
    """Get resource service with dependencies"""
    return ResourceService(resource_repository=resource_repository)

def get_role_service(
    role_repository: RoleRepository = Depends(get_role_repository),
    resource_service: ResourceService = Depends(get_resource_service),
) -> RoleService:
    """Get role service with dependencies"""
    return RoleService(
        role_repository=role_repository, 
        resource_service=resource_service
    )

def get_user_service(
    auth_service: AuthenticationService = Depends(get_auth_service),
    user_repository: UserRepository = Depends(get_user_repository),
    role_service: RoleService = Depends(get_role_service)
) -> UserService:
    """Get user service with dependencies"""
    return UserService(
        authentication_service=auth_service, 
        user_repository=user_repository,
        role_service=role_service
    )

def get_farmer_service(
    farmer_repository: FarmerRepository = Depends(get_farmer_repository)
) -> FarmerService:
    """Get farmer service with dependencies"""
    return FarmerService(farmer_repository=farmer_repository)

def get_biodata_service(
    farmer_service: FarmerService = Depends(get_farmer_service),
    biodata_repository: BiodataRepository = Depends(get_biodata_repository),
) -> BiodataService:
    """Get biodata service with dependencies"""
    return BiodataService(
        farmer_service=farmer_service, 
        biodata_repository=biodata_repository
    )


def get_warehouse_service(
    user_service: UserService = Depends(get_user_service),
    warehouse_repository: WarehouseRepository = Depends(get_warehouse_repository),
) -> WarehouseService:
    """Get warehouse service with dependencies"""
    return WarehouseService(
        user_service=user_service, 
        warehouse_repository=warehouse_repository
    )

def get_product_service(
    biodata_service: BiodataService = Depends(get_biodata_service),
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
    product_repository: ProductRepository = Depends(get_product_repository),
) -> ProductService:
    """Get product service with dependencies"""
    return ProductService(
        product_repository=product_repository, 
        crop_service=biodata_service, 
        warehouse_service=warehouse_service
    )

def get_employee_service(
    employee_repository: EmployeeRepository = Depends(get_employee_repository)
) -> EmployeeService:
    """Get employee service with dependencies"""
    return EmployeeService(employee_repository=employee_repository)

def get_tax_service(
    tax_repository: TaxRepository = Depends(get_tax_repository)
) -> TaxService:
    return TaxService(tax_repository=tax_repository)


AuthServiceDep = Annotated[AuthenticationService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
FarmerServiceDep = Annotated[FarmerService, Depends(get_farmer_service)]
BiodataServiceDep = Annotated[BiodataService, Depends(get_biodata_service)]
ResourceServiceDep = Annotated[ResourceService, Depends(get_resource_service)]
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
WarehouseServiceDep = Annotated[WarehouseService, Depends(get_warehouse_service)]
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
TaxServiceDep = Annotated[TaxService, Depends(get_tax_service)]