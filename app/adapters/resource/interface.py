from abc import ABC, abstractmethod
from typing import Optional, List
from app.adapters.resource.models import ResourceDBSchema, ResourceCreate

class IResourceRepository(ABC):
    @abstractmethod
    def create_resource(self, resource_data: ResourceCreate) -> ResourceDBSchema:
        pass

    @abstractmethod
    def get_resource_by_id(self, resource_id: str) -> Optional[ResourceDBSchema]:
        pass

    @abstractmethod
    def get_resource_by_role_id(self, role_id: str) -> Optional[ResourceDBSchema]:
        pass

    @abstractmethod
    def get_all_resources(self) -> List[ResourceDBSchema]:
        pass

    @abstractmethod
    def update_resource(self, resource_id: str, update_data: ResourceCreate) -> ResourceDBSchema:
        pass

    @abstractmethod
    def delete_resource(self, resource_id: str) -> None:
        pass
