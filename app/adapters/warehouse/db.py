from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.adapters.warehouse.interface import IWarehouseRepository
from app.adapters.warehouse.models import (
    Warehouse, 
    WarehouseCreate, 
    WarehouseDBSchema, 
    UserWarehouse
)
from app.adapters.user.models import UserModel


class WarehouseRepository(IWarehouseRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_warehouse(self, warehouse_data: WarehouseCreate) -> WarehouseDBSchema:
        db_warehouse = Warehouse(**warehouse_data.model_dump())
        self.db.add(db_warehouse)
        self.db.commit()
        self.db.refresh(db_warehouse)
        return WarehouseDBSchema.model_validate(db_warehouse)

    def get_warehouse_by_id(self, warehouse_id: UUID) -> Optional[WarehouseDBSchema]:
        db_warehouse = self.db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if db_warehouse:
            return WarehouseDBSchema.model_validate(db_warehouse)
        return None

    def get_warehouse_by_name(self, name: str) -> Optional[WarehouseDBSchema]:
        db_warehouse = self.db.query(Warehouse).filter(Warehouse.name == name).first()
        if db_warehouse:
            return WarehouseDBSchema.model_validate(db_warehouse)
        return None

    def get_all_warehouses(self) -> List[WarehouseDBSchema]:
        db_warehouses = self.db.query(Warehouse).all()
        return [WarehouseDBSchema.model_validate(warehouse) for warehouse in db_warehouses]

    def update_warehouse(self, warehouse_id: str, update_data: WarehouseCreate) -> WarehouseDBSchema:
        db_warehouse = self.db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not db_warehouse:
            raise ValueError('Warehouse not found')
        for key, value in update_data.model_dump().items():
            setattr(db_warehouse, key, value)
        self.db.commit()
        self.db.refresh(db_warehouse)
        return WarehouseDBSchema.model_validate(db_warehouse)

    def delete_warehouse(self, warehouse_id: str) -> None:
        db_warehouse = self.db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if db_warehouse:
            db_warehouse.is_deleted=True
            self.db.commit()

    def assign_agent(self, agent_id: str, warehouse_id: str):
        warehouse_uuid = UUID(warehouse_id)
        user_uuid = UUID(agent_id)
        existing = self.db.query(UserWarehouse).filter_by(warehouse_id=warehouse_uuid, user_id=user_uuid).first()
        if not existing:
            db_warehouse_resource = UserWarehouse(warehouse_id=warehouse_uuid, user_id=user_uuid)
            self.db.add(db_warehouse_resource)
            self.db.commit()

        else:
            existing.is_deleted=True
            self.db.commit()

    def unassign_agent(self, user_id: str, warehouse_id: str):
        warehouse_uuid = UUID(warehouse_id)
        user_uuid = UUID(user_id)
        db_warehouse_resource = self.db.query(UserWarehouse).filter_by(warehouse_id=warehouse_uuid, user_id=user_uuid).first()
        if db_warehouse_resource:
            db_warehouse_resource.is_deleted=True
            self.db.commit()

    def get_assigned_agent(self, warehouse_id: str):
        warehouse_uuid = UUID(warehouse_id)
        users = (
            self.db.query(UserModel)
            .join(UserWarehouse, UserModel.id == UserWarehouse.user_id)
            .filter(UserWarehouse.warehouse_id == warehouse_uuid)
            .all()
        )
        return users
        

