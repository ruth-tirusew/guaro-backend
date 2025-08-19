from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from app.modules.resources.schemas import ResourceRead
from app.modules.roles.service import RoleService
from app.modules.roles.schemas import RoleCreate, RoleRead, RoleUpdate
from app.utils.middlewares.authorization import (
    require_auth, 
    require_role_management, 
    require_admin_role,
    require_manager_role
)
from app.core.exceptions import ErrorFactory
from app.dependencies import RoleServiceDep

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_service: RoleServiceDep,
    role: RoleCreate,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_role_management()),
):
    """Create a new role - requires role management permission"""
    try:
        return role_service.create_role(role)
    except ValueError as e:
        raise ErrorFactory.validation_error(
            field="role_data",
            value=str(role),
            user_message=str(e),
            context={"operation": "create_role", "role_data": role.model_dump()}
        )
    except Exception as e:
        raise ErrorFactory.internal_server_error(
            user_message="Failed to create role. Please try again later.",
            log_message=f"Role creation failed: {str(e)}",
            context={"operation": "create_role", "role_data": role.model_dump(), "error": str(e)}
        )

@router.get("/", response_model=List[RoleRead])
async def get_all_roles(
    role_service: RoleServiceDep,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_manager_role()),
):
    """Get all roles - requires manager role or higher"""
    try:
        roles = role_service.get_all_roles()
        return [RoleRead.model_validate(r) for r in roles]
    except Exception as e:
        raise ErrorFactory.internal_server_error(
            user_message="Failed to retrieve roles. Please try again later.",
            log_message=f"Role retrieval failed: {str(e)}",
            context={"operation": "get_all_roles", "error": str(e)}
        )

@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_service: RoleServiceDep,
    role_id: str,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_manager_role()),
):
    """Get a specific role by ID - requires manager role or higher"""
    try:
        role = role_service.get_role_by_id(role_id)
        if not role:
            raise ErrorFactory.not_found(
                resource="Role",
                user_message=f"Role with ID {role_id} not found",
                context={"role_id": role_id}
            )
        return RoleRead.model_validate(role)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise ErrorFactory.internal_server_error(
            user_message="Failed to retrieve role. Please try again later.",
            log_message=f"Role retrieval failed: {str(e)}",
            context={"operation": "get_role", "role_id": role_id, "error": str(e)}
        )

@router.put("/{role_id}", response_model=RoleRead)
async def update_role(
    role_service: RoleServiceDep,
    role_id: str, 
    role_update: RoleUpdate,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_role_management()),
):
    """Update a role - requires role management permission"""
    try:
        role = role_service.update_role(role_id, role_update)
        if not role:
            raise ErrorFactory.not_found(
                resource="Role",
                user_message=f"Role with ID {role_id} not found",
                context={"role_id": role_id}
            )
        return RoleRead.model_validate(role)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise ErrorFactory.internal_server_error(
            user_message="Failed to update role. Please try again later.",
            log_message=f"Role update failed: {str(e)}",
            context={"operation": "update_role", "role_id": role_id, "error": str(e)}
        )

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_service: RoleServiceDep,
    role_id: str,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_role_management()),
):
    """Delete a role - requires role management permission"""
    try:
        role_service.delete_role(role_id)
    except Exception as e:
        raise ErrorFactory.internal_server_error(
            user_message="Failed to delete role. Please try again later.",
            log_message=f"Role deletion failed: {str(e)}",
            context={"operation": "delete_role", "role_id": role_id, "error": str(e)}
        )

@router.post("/{role_id}/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_resource_to_role(
    role_service: RoleServiceDep,
    role_id: str, 
    resource_id: str,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_role_management()),
):
    """Assign a resource to a role - requires role management permission"""
    try:
        role_service.assign_resource_to_role(role_id, resource_id)
    except Exception as e:
        raise ErrorFactory.internal_server_error(
            user_message="Failed to assign resource to role. Please try again later.",
            log_message=f"Resource assignment failed: {str(e)}",
            context={"operation": "assign_resource_to_role", "role_id": role_id, "resource_id": resource_id, "error": str(e)}
        )

@router.delete("/{role_id}/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_resource_from_role(
    role_service: RoleServiceDep,
    role_id: str, 
    resource_id: str,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_role_management()),
):
    """Unassign a resource from a role - requires role management permission"""
    try:
        role_service.unassign_resource_from_role(role_id, resource_id)
    except Exception as e:
        raise ErrorFactory.internal_server_error(
            user_message="Failed to unassign resource from role. Please try again later.",
            log_message=f"Resource unassignment failed: {str(e)}",
            context={"operation": "unassign_resource_from_role", "role_id": role_id, "resource_id": resource_id, "error": str(e)}
        )

@router.get("/{role_id}/resources", response_model=List[ResourceRead])
async def get_resources_for_role(
    role_service: RoleServiceDep,
    role_id: str,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_manager_role()),
):
    """Get all resources assigned to a role - requires manager role or higher"""
    try:
        resources = role_service.get_resources_for_role(role_id)
        return [ResourceRead.model_validate(r) for r in resources]
    except Exception as e:
        raise ErrorFactory.internal_server_error(
            user_message="Failed to retrieve role resources. Please try again later.",
            log_message=f"Role resources retrieval failed: {str(e)}",
            context={"operation": "get_resources_for_role", "role_id": role_id, "error": str(e)}
        )
