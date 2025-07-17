from typing import List, Optional
from uuid import uuid4
from app.adapters.role.interface import IRoleRepository
from app.adapters.role.models import RoleDBSchema, RoleCreate

class MockRoleRepository(IRoleRepository):
    def __init__(self):
        self.roles = []

    def create_role(self, role_data: RoleCreate) -> RoleDBSchema:
        role = RoleDBSchema(id=str(uuid4()), **role_data.model_dump())
        self.roles.append(role)
        return role

    def get_role_by_id(self, role_id: str) -> Optional[RoleDBSchema]:
        for role in self.roles:
            if role.id == role_id:
                return role
        return None

    def get_role_by_name(self, name: str) -> Optional[RoleDBSchema]:
        for role in self.roles:
            if role.name == name:
                return role
        return None

    def get_all_roles(self) -> List[RoleDBSchema]:
        return list(self.roles)

    def update_role(self, role_id: str, update_data: RoleCreate) -> RoleDBSchema:
        for idx, role in enumerate(self.roles):
            if role.id == role_id:
                updated_role = role.model_copy(update=update_data.model_dump())
                self.roles[idx] = updated_role
                return updated_role
        raise ValueError('Role not found')

    def delete_role(self, role_id: str) -> None:
        self.roles = [role for role in self.roles if role.id != role_id]

    def assign_role_to_resource(self, resource_id: str, role_id: str):
        if not hasattr(self, "role_resource_assignments"):
            self.role_resource_assignments = []
        if (role_id, resource_id) not in self.role_resource_assignments:
            self.role_resource_assignments.append((role_id, resource_id))

    def unassign_role_to_resource(self, resource_id: str, role_id: str):
        if hasattr(self, "role_resource_assignments"):
            self.role_resource_assignments = [
                (r_id, res_id)
                for (r_id, res_id) in self.role_resource_assignments
                if not (r_id == role_id and res_id == resource_id)
            ]

    def get_assigned_resources(self, role_id: str):
        if not hasattr(self, "role_resource_assignments"):
            self.role_resource_assignments = []
        return [
            resource_id
            for (r_id, resource_id) in self.role_resource_assignments
            if r_id == role_id
        ]
