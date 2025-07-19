from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.container import get_container
from app.modules.resources.schemas import ResourceRead
from app.modules.roles.service import RoleService
from app.modules.roles.schemas import RoleCreate, RoleRead, RoleUpdate  # Assuming these exist

router = APIRouter(prefix="/roles", tags=["Roles"])

container = get_container()
role_service: RoleService = container.resolve("role_service")

@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate):
    try:
        return role_service.create_role(role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[RoleRead])
def get_all_roles():
    try:
        roles = role_service.get_all_roles()
        return [RoleRead.model_validate(r) for r in roles]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{role_id}", response_model=RoleRead)
def get_role(role_id: str):
    role = role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return RoleRead.model_validate(role)

@router.put("/{role_id}", response_model=RoleRead)
def update_role(role_id: str, role_update: RoleUpdate):
    role = role_service.update_role(role_id, role_update)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return RoleRead.model_validate(role)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: str):
    try:
        role_service.delete_role(role_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{role_id}/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def assign_resource_to_role(role_id: str, resource_id: str):
    try:
        role_service.assign_resource_to_role(role_id, resource_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{role_id}/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def unassign_resource_from_role(role_id: str, resource_id: str):
    try:
        role_service.unassign_resource_from_role(role_id, resource_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{role_id}/resources", response_model=List[ResourceRead])
def get_resources_for_role(role_id: str):
    resources = role_service.get_resources_for_role(role_id)
    return [ResourceRead.model_validate(r) for r in resources]
