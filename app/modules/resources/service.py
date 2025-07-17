from app.adapters.resource.interface import IResourceRepository
from app.adapters.resource.models import ResourceCreate
from app.modules.resources.schemas import ResourceRead, ResourceList
from typing import Optional, List
import uuid

class ResourceService:
    def __init__(self, resource_repository: IResourceRepository):
        self.repository = resource_repository

    def create_resource(self, resource_data: ResourceCreate) -> ResourceRead:
        resource = self.repository.create_resource(resource_data)
        return ResourceRead.model_validate(resource)

    def get_resource(self, resource_id: str) -> Optional[ResourceRead]:
        resource = self.repository.get_resource_by_id(resource_id)
        if resource and hasattr(resource, 'id') and isinstance(resource.id, uuid.UUID):
            resource.id = str(resource.id)
        return ResourceRead.model_validate(resource) if resource else None

    def list_resources(self) -> ResourceList:
        resources = self.repository.get_all_resources()
        for resource in resources:
            if hasattr(resource, 'id') and isinstance(resource.id, uuid.UUID):
                resource.id = str(resource.id)
        return ResourceList(resources=[ResourceRead.model_validate(r) for r in resources])

    def update_resource(self, resource_id: str, update_data: ResourceCreate) -> Optional[ResourceRead]:
        resource = self.repository.update_resource(resource_id, update_data)
        if resource and hasattr(resource, 'id') and isinstance(resource.id, uuid.UUID):
            resource.id = str(resource.id)
        return ResourceRead.model_validate(resource) if resource else None

    def delete_resource(self, resource_id: str) -> bool:
        self.repository.delete_resource(resource_id)
        return True
