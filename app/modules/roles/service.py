from typing import List, Optional

from app.adapters.role.interface import IRoleRepository
from app.modules.resources.service import ResourceService
from app.adapters.role.models import RoleDBSchema, RoleCreate
from app.modules.roles.schemas import RoleRead
from app.adapters.resource.models import ResourceDBSchema

class RoleService:
    def __init__(self, role_repository: IRoleRepository, resource_service: ResourceService):
        self.repository = role_repository
        self.resource_service = resource_service

    def create_role(self, role_data: RoleCreate) -> RoleDBSchema:
        return self.repository.create_role(role_data)

    def get_role_by_id(self, role_id: str) -> Optional[RoleRead]:
        return RoleRead.from_orm(self.repository.get_role_by_id(role_id))

    def get_all_roles(self) -> List[RoleDBSchema]:
        return self.repository.get_all_roles()

    def update_role(self, role_id: str, update_data: RoleCreate) -> RoleDBSchema:
        return self.repository.update_role(role_id, update_data)

    def delete_role(self, role_id: str) -> None:
        self.repository.delete_role(role_id)

    def assign_resource_to_role(self, role_id: str, resource_id: str) -> None:
        self.repository.assign_role_to_resource(resource_id=resource_id, role_id=role_id)

    def unassign_resource_from_role(self, role_id: str, resource_id: str) -> None:
        self.repository.unassign_role_to_resource(resource_id=resource_id, role_id=role_id)

    def get_resources_for_role(self, role_id: str) -> List[ResourceDBSchema]:
        assigned_resources = self.repository.get_assigned_resources(role_id)
        return assigned_resources
        
      
