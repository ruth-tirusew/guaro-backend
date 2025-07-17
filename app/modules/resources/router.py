from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.container import get_container
from app.modules.resources.schemas import ResourceCreate, ResourceRead, ResourceList


router = APIRouter(prefix="/resource", tags=["Resources"])

container = get_container()
resource_service = container.resolve("resource_service")

@router.post("/", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource(resource: ResourceCreate):
    try:
        return resource_service.create_resource(resource)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{resource_id}", response_model=ResourceRead)
def get_resource(resource_id: str):
    resource = resource_service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return resource


@router.get("/", response_model=ResourceList)
def list_resources():
    return resource_service.list_resources()

@router.put("/{resource_id}", response_model=ResourceRead)
def update_resource(resource_id: str, resource_update: ResourceCreate):
    resource = resource_service.update_resource(resource_id, resource_update)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return resource

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: str):
    resource_service.delete_resource(resource_id)
    return None
