from sqlalchemy.orm import Session
from app.adapters.role.interface import IRoleRepository
from app.adapters.role.models import Role, RoleDBSchema, RoleCreate
from typing import List, Optional
from uuid import UUID

class DBRoleRepository(IRoleRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role_data: RoleCreate) -> RoleDBSchema:
        db_role = Role(**role_data.model_dump())
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return RoleDBSchema.model_validate(db_role)

    def get_role_by_id(self, role_id: str) -> Optional[RoleDBSchema]:
        db_role = self.db.query(Role).filter(Role.id == role_id).first()
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
