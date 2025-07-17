from sqlalchemy.orm import Session
from app.adapters.role.interface import IRoleRepository
from app.adapters.role.models import Role, RoleDBSchema, RoleCreate, RoleResource
from app.adapters.resource.models import Resource
from typing import List, Optional
from uuid import UUID

class RoleRepository(IRoleRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role_data: RoleCreate) -> RoleDBSchema:
        db_role = Role(**role_data.model_dump())
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return RoleDBSchema.model_validate(db_role)

    def get_role_by_id(self, role_id: str) -> Optional[RoleDBSchema]:
        uuid_obj = UUID(role_id)
        db_role = self.db.query(Role).filter(Role.id == uuid_obj).first()
        if db_role:
            return RoleDBSchema.model_validate(db_role)
        return None

    def get_role_by_name(self, name: str) -> Optional[RoleDBSchema]:
        db_role = self.db.query(Role).filter(Role.name == name).first()
        if db_role:
            return RoleDBSchema.model_validate(db_role)
        return None

    def get_all_roles(self) -> List[RoleDBSchema]:
        db_roles = self.db.query(Role).all()
        return [RoleDBSchema.model_validate(role) for role in db_roles]

    def update_role(self, role_id: str, update_data: RoleCreate) -> RoleDBSchema:
        db_role = self.db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            raise ValueError('Role not found')
        for key, value in update_data.model_dump().items():
            setattr(db_role, key, value)
        self.db.commit()
        self.db.refresh(db_role)
        return RoleDBSchema.model_validate(db_role)

    def delete_role(self, role_id: str) -> None:
        db_role = self.db.query(Role).filter(Role.id == role_id).first()
        if db_role:
            self.db.delete(db_role)
            self.db.commit()

    def assign_role_to_resource(self, resource_id: str, role_id: str):
        role_uuid = UUID(role_id)
        resource_uuid = UUID(resource_id)
        existing = self.db.query(RoleResource).filter_by(role_id=role_uuid, resource_id=resource_uuid).first()
        if not existing:
            db_role_resource = RoleResource(role_id=role_uuid, resource_id=resource_uuid)
            self.db.add(db_role_resource)
            self.db.commit()

    def unassign_role_to_resource(self, resource_id: str, role_id: str):
        role_uuid = UUID(role_id)
        resource_uuid = UUID(resource_id)
        db_role_resource = self.db.query(RoleResource).filter_by(role_id=role_uuid, resource_id=resource_uuid).first()
        if db_role_resource:
            self.db.delete(db_role_resource)
            self.db.commit()

    def get_assigned_resources(self, role_id: str):
        resources = (
            self.db.query(Resource)
            .join(RoleResource, Resource.id == RoleResource.resource_id)
            .filter(RoleResource.role_id == role_id)
            .all()
        )
        return resources
        

