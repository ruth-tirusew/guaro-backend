from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.adapters.role.interface import IRoleRepository
from app.modules.resources.service import ResourceService
from app.adapters.role.models import RoleDBSchema, RoleCreate
from app.modules.roles.schemas import RoleRead
from app.adapters.resource.models import ResourceDBSchema
from app.modules.roles.errors import  NotFoundError

class RoleService:
    def __init__(self, role_repository: IRoleRepository, resource_service: ResourceService):
        self.repository = role_repository
        self.resource_service = resource_service

    def create_role(self, role_data: RoleCreate) -> RoleDBSchema:
        if self._role_name_exists(role_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_data.name}' already exists"
            )
    
        if not self._is_valid_role_name(role_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name must be alphanumeric and between 3-50 characters"
            )
        
        return self.repository.create_role(role_data)

    def get_role_by_user_id(self, user_id: UUID) -> RoleRead:
        role = self.repository.get_role_by_user_id(user_id)
        return role

    def get_role_by_id(self, role_id: str) -> RoleRead:
        role = self.repository.get_role_by_id(role_id)
        if not role:
            raise NotFoundError
        return RoleRead.from_orm(role)

    def assign_resource_to_role(self, role_id: str, resource_id: str) -> None:
        role = self.repository.get_role_by_id(role_id)
        if not role:
            raise NotFoundError
    
        resource = self.resource_service.get_resource(resource_id)
        if not resource:
            raise NotFoundError
    
        if self._is_resource_assigned_to_role(role_id, resource_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource is already assigned to role "
            )
        
        self.repository.assign_role_to_resource(resource_id=resource_id, role_id=role_id)

    def unassign_resource_to_role(self, role_id: str, resource_id: str) -> None:
        role = self.repository.get_role_by_id(role_id)
        if not role:
            raise NotFoundError
    
        resource = self.resource_service.get_resource(resource_id)
        if not resource:
            raise NotFoundError
    
        if not self._is_resource_assigned_to_role(role_id, resource_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource is not assigned to role "
            )
        
        self.repository.unassign_role_to_resource(resource_id=resource_id, role_id=role_id)
    
    def assign_role_to_user(self, user_id: UUID, role_id: UUID):
        self.repository.assign_user_role(user_id=user_id, role_id=role_id)

    def get_assigned_resources(self,role_id):
        print("Role ID_____________________")
        print(role_id)
        assigned_resources = self.repository.get_assigned_resources(role_id)
        print(assigned_resources)
        return assigned_resources
        
    def _role_name_exists(self, name: str) -> bool:
        return self.repository.get_role_by_name(name) is not None

    def _is_valid_role_name(self, name: str) -> bool:
        return name.isalnum() and 3 <= len(name) <= 50

    def _is_resource_assigned_to_role(self, role_id: str, resource_id: str) -> bool:
        assigned_resources = self.repository.get_assigned_resources(role_id)
        return any(r.id == resource_id for r in assigned_resources)