from typing import List, Optional

from app.adapters.warehouse.interface import IWarehouseRepository
from app.modules.users.service import UserService

from app.modules.warehouse.errors import NotFoundError
from app.modules.warehouse.schema import (
    WarehouseCreate, 
    Warehouse, 
    WarehouseList,
    AgentsList,
    AssignedAgent
)

class WarehouseService:
    def __init__(self, user_service: UserService, warehouse_repository: IWarehouseRepository):
        self.user_service = user_service
        self.repository = warehouse_repository
    def get_all_warehouses(self)->WarehouseList:
        warehouses = self.repository.get_all_warehouses()
        return WarehouseList(warehouses=[Warehouse.model_validate(w.dict()) for w in warehouses]) 

    def get_warehouse_by_id(self, warehouse_id:str)->Warehouse:
        warehouse = self.repository.get_warehouse_by_id(warehouse_id=warehouse_id)
        if not warehouse:
            raise NotFoundError
        return Warehouse.from_orm(warehouse)

    def create_warehouse(self, data: WarehouseCreate):
        return self.repository.create_warehouse(data)

    def update_warehouse(self, data: Warehouse):
        self.get_warehouse_by_id(data.id)
        return self.repository.update_warehouse(data.id, data)

    def delete_warehouse(self, warehouse_id: str):
        self.get_warehouse_by_id(warehouse_id=warehouse_id)
        self.repository.delete_warehouse(warehouse_id=warehouse_id)

    def assign_agent(self, agent_id: str, warehouse_id:str):
        print(agent_id)
        user = self.user_service.get_user(agent_id)
        if not user:
            raise NotFoundError
        response = self.repository.assign_agent(warehouse_id=warehouse_id, agent_id=agent_id)
    
    def unassign_agent(self, agent_id: str, warehouse_id:str):
        if not user:
            raise NotFoundError
        response = self.repository.unassign_agent(warehouse_id=warehouse_id, agent_id=agent_id)

    def get_assigned_agent(self, warehouse_id: str):
        warehouse = self.repository.get_warehouse_by_id(warehouse_id=warehouse_id)
        if  not warehouse:
            raise NotFoundError
        agents = self.repository.get_assigned_agent(warehouse_id=warehouse_id)
        return AgentsList(agents=[AssignedAgent.from_orm(a) for a in  agents])
    

