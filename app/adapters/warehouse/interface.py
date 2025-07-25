from abc import ABC, abstractmethod
from typing import Optional, List
from app.adapters.warehouse.models import WarehouseCreate, WarehouseDBSchema

class IWarehouseRepository(ABC):

    @abstractmethod
    def create_warehouse(self, warehouse_data: WarehouseCreate) -> WarehouseDBSchema:
        pass

    @abstractmethod
    def get_warehouse_by_id(self, warehouse_id: str) -> Optional[WarehouseDBSchema]:
        pass

    @abstractmethod
    def get_all_warehouses(self) -> List[WarehouseDBSchema]:
        pass

    @abstractmethod
    def update_warehouse(self, warehouse_id: str, update_data: WarehouseCreate) -> WarehouseDBSchema:
        pass

    @abstractmethod
    def delete_warehouse(self, warehouse_id: str) -> None:
        pass
    
    @abstractmethod
    def assign_agent(self, warehouse_id: str, agent_id: str)-> WarehouseDBSchema:
        pass

    @abstractmethod
    def unassign_agent(self, warehouse_id: str, agent_id: str) -> WarehouseDBSchema:
        pass
    @abstractmethod
    def get_assigned_agent(self, warehouse_id: str):
        pass


