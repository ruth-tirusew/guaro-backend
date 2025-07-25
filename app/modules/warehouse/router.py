from fastapi import APIRouter, HTTPException, status
from app.container import get_container
from app.modules.warehouse.schema import Warehouse, WarehouseCreate, WarehouseList, AgentsList

router = APIRouter(prefix="/warehouse", tags=["Warehouse"])

container = get_container()
warehouse_service = container.resolve("warehouse_service")

@router.post("/", response_model=Warehouse, status_code=status.HTTP_201_CREATED)
def create_warehouse(data: WarehouseCreate):
    try:
        return warehouse_service.create_warehouse(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", status_code=status.HTTP_200_OK, response_model=WarehouseList)
def get_all_warehouses():
    return warehouse_service.get_all_warehouses()

@router.get("/{id}", response_model=Warehouse, status_code=status.HTTP_200_OK)
def get_warehouse_by_id(id: str):
    return warehouse_service.get_warehouse_by_id(id)

@router.put("/", response_model=Warehouse, status_code=status.HTTP_200_OK)
def update_warehouse(data: Warehouse):
    return warehouse_service.update_warehouse(data)

@router.put("/{warehouse_id}/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def assign_agent(
    warehouse_id: str, 
    agent_id: str
):
    return warehouse_service.assign_agent(agent_id, warehouse_id)

@router.get("/{id}/agent",response_model=AgentsList, status_code=status.HTTP_200_OK)
def get_assigned_agent(id: str):
    return warehouse_service.get_assigned_agent(id)

