from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.modules.resources.schemas import ResourceCreate, ResourceRead, ResourceList
from app.utils.middlewares.authorization import (
    require_auth, 
    require_resource_management, 
    require_manager_role,
    require_read_permission
)
from app.core.exceptions import ErrorFactory
from app.dependencies import ResourceServiceDep
from app.modules.resources.service import ResourceService

router = APIRouter(prefix="/resource", tags=["Resources"])

@router.post("/", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource_service:ResourceServiceDep,
    resource: ResourceCreate,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_resource_management()),
):
    try:
        return resource_service.create_resource(resource)
    except Exception as e:
        raise ErrorFactory.internal_error(
            user_message="Failed to create resource. Please try again later.",
            log_message=f"Resource creation failed: {str(e)}",
            context={
                "operation": "create_resource", 
                "resource_data": resource.model_dump(), 
                "error": str(e)
            }
        )

@router.get("/{resource_id}", response_model=ResourceRead)
async def get_resource(
    resource_service:ResourceServiceDep,
    resource_id: str,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_manager_role()),
):
    """Get a specific resource by ID - requires manager role or higher"""
    try:
        resource = resource_service.get_resource(resource_id)
        if not resource:
            raise ErrorFactory.not_found(
                resource="Resource",
                user_message=f"Resource with ID {resource_id} not found",
                context={"resource_id": resource_id}
            )
        return resource
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise ErrorFactory.internal_error(
            user_message="Failed to retrieve resource. Please try again later.",
            log_message=f"Resource retrieval failed: {str(e)}",
            context={"operation": "get_resource", "resource_id": resource_id, "error": str(e)}
        )

@router.get("/", response_model=ResourceList)
async def list_resources(
    resource_service:ResourceServiceDep,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_resource_management()),
):
    """List all resources - requires manager role or higher"""
    try:
        return resource_service.list_resources()
    except Exception as e:
        raise ErrorFactory.internal_error(
            user_message="Failed to retrieve resources. Please try again later.",
            log_message=f"Resource listing failed: {str(e)}",
            context={"operation": "list_resources", "error": str(e)}
        )

@router.put("/{resource_id}", response_model=ResourceRead)
async def update_resource(
    resource_service:ResourceServiceDep,
    resource_id: str, 
    resource_update: ResourceCreate,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_resource_management()),
):
    """Update a resource - requires resource management permission"""
    try:
        resource = resource_service.update_resource(resource_id, resource_update)
        if not resource:
            raise ErrorFactory.not_found(
                resource="Resource",
                user_message=f"Resource with ID {resource_id} not found",
                context={"resource_id": resource_id}
            )
        return resource
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise ErrorFactory.internal_error(
            user_message="Failed to update resource. Please try again later.",
            log_message=f"Resource update failed: {str(e)}",
            context={"operation": "update_resource", "resource_id": resource_id, "error": str(e)}
        )

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_service:ResourceServiceDep,
    resource_id: str,
    request: Request,
    user_info: dict = Depends(require_auth()),
    _: None = Depends(require_resource_management()),
):
    """Delete a resource - requires resource management permission"""
    try:
        resource_service.delete_resource(resource_id)
        return None
    except Exception as e:
        raise ErrorFactory.internal_error(
            user_message="Failed to delete resource. Please try again later.",
            log_message=f"Resource deletion failed: {str(e)}",
            context={"operation": "delete_resource", "resource_id": resource_id, "error": str(e)}
        )
