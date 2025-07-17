from typing import Dict, Any

from app.adapters.resource.interface import IResourceRepository

class ResourceService:
    def __init__(self, resource_repository: IResourceRepository):
        self.repository = resource_repository
