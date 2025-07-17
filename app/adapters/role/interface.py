from abc import ABC, abstractmethod
from typing import Optional, List
from app.adapters.role.models import RoleDBSchema, RoleCreate

class IRoleRepository(ABC):
    @abstractmethod
    def create_role(self, role_data: RoleCreate) -> RoleDBSchema:
        pass

    @abstractmethod
    def get_role_by_id(self, role_id: str) -> Optional[RoleDBSchema]:
        pass

    @abstractmethod
    def get_all_roles(self) -> List[RoleDBSchema]:
        pass

    @abstractmethod
    def update_role(self, role_id: str, update_data: RoleCreate) -> RoleDBSchema:
        pass

    @abstractmethod
    def delete_role(self, role_id: str) -> None:
        pass
