from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
import uuid

from app.modules.users.schemas import (
    UserCreate, 
    UserUpdate, 
    UserRead, 
    UserList
)
from app.dependencies import UserServiceDep
from app.utils.middlewares.authorization import (
    require_auth,
    require_user_management,
    require_admin_role,
    require_manager_role,
    require_permission
)
from app.core.exceptions import ErrorFactory
from app.logging import logger

router = APIRouter(prefix="/users", tags=["Users"])

# User CRUD Operations
@router.post(
    "/", 
    response_model=UserRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account with authentication service integration"
)
def create_user(
    user: UserCreate, 
    user_service: UserServiceDep,
    # _: dict = Depends(require_user_management())
):
    """Create a new user - requires user management permissions"""
    logger.info(f"Creating new user with email: {user.email}")
    return user_service.create_user(user)
   
@router.get(
    "/{user_id}", 
    response_model=UserRead,
    summary="Get user by ID",
    description="Retrieve a user by their unique identifier"
)
def get_user(
    user_id: str, 
    user_service: UserServiceDep,
    current_user: dict = Depends(require_auth())
):
    """Get user by ID - requires authentication"""
    return user_service.get_user(user_id)
    
@router.get(
    "/by-email/{email}", 
    response_model=UserRead,
    summary="Get user by email",
    description="Retrieve a user by their email address"
)
def get_user_by_email(
    email: str, 
    user_service: UserServiceDep,
    _: dict = Depends(require_permission("users", "read"))
):
    """Get user by email - requires read permission"""
    return user_service.get_user_by_email(email)
   

@router.get(
    "/", 
    response_model=UserList,
    summary="List all users",
    description="Retrieve a list of all users with optional pagination"
)
def list_users(
    user_service: UserServiceDep,
    _: dict = Depends(require_permission("users", "read"))
):
    """List users with optional pagination - requires read permission"""
    try:
        return user_service.list_users()
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.put(
    "/{user_id}", 
    response_model=UserRead,
    summary="Update user",
    description="Update user information"
)
def update_user(
    user_id: str, 
    user_update: UserUpdate, 
    user_service: UserServiceDep,
    current_user: dict = Depends(require_auth())
):
    """Update user - requires authentication (users can update themselves or admins can update any user)"""
    current_user_id = current_user.get('sub') or current_user.get('user_id')
    current_user_obj = user_service.get_user_by_provider_id(current_user_id)
        
    if not current_user_obj or str(current_user_obj.id) != user_id:
        try:
            require_user_management()(current_user)
        except HTTPException as err:
            raise ErrorFactory.forbidden(
                user_message="You can only update your own profile or you need user management privileges"
            ) from err
                
    return user_service.update_user(user_id, user_update)

@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account"
)
def delete_user(
    user_id: str, 
    user_service: UserServiceDep,
    # _: dict = Depends(require_admin_role())
):
    """Delete user - requires admin role"""
    user_service.delete_user(user_id)

@router.post(
    "/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign role to user",
    description="Assign a specific role to a user"
)
def assign_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    user_service: UserServiceDep,
    _: dict = Depends(require_admin_role())
):
    """Assign role to user - requires admin role"""
    user_service.assign_user_role(user_id, role_id)