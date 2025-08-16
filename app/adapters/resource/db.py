import uuid
from sqlalchemy.orm import Session
from app.adapters.resource.interface import IResourceRepository
from app.adapters.resource.models import Resource, ResourceDBSchema, ResourceCreate
from typing import List, Optional

class ResourceRepository(IResourceRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_resource(self, resource_data: ResourceCreate) -> ResourceDBSchema:
        db_resource = Resource(**resource_data.model_dump())
        self.db.add(db_resource)
        self.db.commit()
        self.db.refresh(db_resource)
        return ResourceDBSchema.model_validate(db_resource)

    def get_resource_by_id(self, resource_id: str) -> Optional[ResourceDBSchema]:
        uuid_obj = uuid.UUID(resource_id)
        db_resource = self.db.query(Resource).filter(Resource.id == uuid_obj).first()
        if db_resource:
            return ResourceDBSchema.model_validate(db_resource)
        return None

    def get_all_resources(self) -> List[ResourceDBSchema]:
        db_resources = self.db.query(Resource).all()
        return [ResourceDBSchema.model_validate(resource) for resource in db_resources]

    def update_resource(self, resource_id: str, update_data: ResourceCreate) -> ResourceDBSchema:
        uuid_obj = uuid.UUID(resource_id)
        db_resource = self.db.query(Resource).filter(Resource.id == uuid_obj).first()
        if not db_resource:
            raise ValueError('Resource not found')
        for key, value in update_data.model_dump().items():
            setattr(db_resource, key, value)
        self.db.commit()
        self.db.refresh(db_resource)
        return ResourceDBSchema.model_validate(db_resource)

    def delete_resource(self, resource_id: str) -> None:
        uuid_obj = uuid.UUID(resource_id)
        db_resource = self.db.query(Resource).filter(Resource.id == uuid_obj).first()
        if db_resource:
            db_resource.is_deleted=True
            self.db.commit()
