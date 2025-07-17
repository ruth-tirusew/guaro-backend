from typing import List, Optional
from uuid import uuid4
from app.adapters.resource.interface import IResourceRepository
from app.adapters.resource.models import ResourceDBSchema, ResourceCreate

class MockResourceRepository(IResourceRepository):
    def __init__(self):
        self.resources = []

    def create_resource(self, resource_data: ResourceCreate) -> ResourceDBSchema:
        resource = ResourceDBSchema(id=str(uuid4()), **resource_data.model_dump())
        self.resources.append(resource)
        return resource

    def get_resource_by_id(self, resource_id: str) -> Optional[ResourceDBSchema]:
        for resource in self.resources:
            if resource.id == resource_id:
                return resource
        return None

    def get_resource_by_role_id(self, role_id: str) -> Optional[ResourceDBSchema]:
        # This is a stub; in a real implementation, you would filter by role-resource mapping
        return next((r for r in self.resources if getattr(r, 'role_id', None) == role_id), None)

    def get_all_resources(self) -> List[ResourceDBSchema]:
        return list(self.resources)

    def update_resource(self, resource_id: str, update_data: ResourceCreate) -> ResourceDBSchema:
        for idx, resource in enumerate(self.resources):
            if resource.id == resource_id:
                updated_resource = resource.model_copy(update=update_data.model_dump())
                self.resources[idx] = updated_resource
                return updated_resource
        raise ValueError('Resource not found')

    def delete_resource(self, resource_id: str) -> None:
        self.resources = [resource for resource in self.resources if resource.id != resource_id]
