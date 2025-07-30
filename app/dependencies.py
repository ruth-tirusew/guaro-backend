from app.container import get_container
from app.modules.authentication.service import AuthenticationService
from app.adapters.authentication.keycloak import KeycloakAdapter
from app.adapters.biodata.db import BiodataRepository
from app.adapters.farmers.db import FarmerRepository
from app.adapters.product.db import ProductRepository
from app.adapters.resource.db import ResourceRepository
from app.adapters.role.db import RoleRepository
from app.adapters.warehouse.db import WarehouseRepository
from app.adapters.user.db import UserRepository

from app.config import settings
from app.modules.biodata.service import BiodataService
from app.modules.farmers.service import FarmerService
from app.modules.products.service import ProductService
from app.modules.resources.service import ResourceService
from app.modules.roles.service import RoleService
from app.modules.warehouse.service import WarehouseService
from app.modules.users.service import UserService

from app.database import get_db

def init_containers():
    container = get_container()
    container.register(
        "auth_adapter",
        lambda: KeycloakAdapter(
            server_url=settings.KEYCLOAK_URL,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            client_secret=settings.KEYCLOAK_CLIENT_SECRET,
            realm=settings.KEYCLOAK_REALM
        )
    )
    container.register("auth_service", lambda: AuthenticationService(container.resolve("auth_adapter")))
    #TODO: Change to factory when registering services
    container.register(
        "user_service",
        lambda: UserService(
            authentication_service=container.resolve("auth_service"),
            user_repository=UserRepository(next(get_db()))
        )
    )

    container.register("farmer_service", lambda: FarmerService(
        farmer_repository= FarmerRepository(next(get_db()))
    ))

    container.register("biodata_service", lambda: BiodataService(
        farmer_service=container.resolve("farmer_service"),
        biodata_repository=BiodataRepository(next(get_db()))
    ))

    container.register(
        "resource_service",
        lambda: ResourceService(
           resource_repository=ResourceRepository(next(get_db()))
        )
    )

    container.register(
        "role_service",
        lambda: RoleService(
           role_repository=RoleRepository(next(get_db())),
           resource_service=container.resolve("resource_service")
        )
    )

    container.register(
        "warehouse_service",
        lambda: WarehouseService(
            user_service=container.resolve("user_service"),
            warehouse_repository=WarehouseRepository(next(get_db()))
        )
    )

    container.register(
        "product_service",
        lambda: ProductService(
            crop_service=container.resolve("biodata_service"),
            product_repository=ProductRepository(next(get_db())),
            warehouse_service=container.resolve("warehouse_service")
        )
    )

    