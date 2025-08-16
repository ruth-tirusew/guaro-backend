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
    _: dict = Depends(require_user_management())
):
    """Create a new user - requires user management permissions"""
    try:
        logger.info(f"Creating new user with email: {user.email}")
        return user_service.create_user(user)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to create user"
        )

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
    try:
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

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
    try:
        user = user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user by email {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.get(
    "/", 
    response_model=UserList,
    summary="List all users",
    description="Retrieve a list of all users with optional pagination"
)
def list_users(
    user_service: UserServiceDep,
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of users to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of users to skip"),
    _: dict = Depends(require_permission("users", "read"))
):
    """List users with optional pagination - requires read permission"""
    try:
        return user_service.list_users(limit=limit, offset=offset)
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
    try:
        # Check if user is updating themselves or has admin privileges
        current_user_id = current_user.get('sub') or current_user.get('user_id')
        current_user_obj = user_service.get_user_by_provider_id(current_user_id)
        
        # Allow users to update themselves or require admin role for updating others
        if not current_user_obj or str(current_user_obj.id) != user_id:
            # Check if user has admin privileges to update other users
            try:
                require_user_management()(current_user)
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own profile or need admin privileges"
                )
        
        user = user_service.update_user(user_id, user_update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to update user"
        )

@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account"
)
def delete_user(
    user_id: str, 
    user_service: UserServiceDep,
    _: dict = Depends(require_admin_role())
):
    """Delete user - requires admin role"""
    try:
        success = user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

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
    # _: dict = Depends(require_admin_role())
):
    """Assign role to user - requires admin role"""
    user_service.assign_user_role(user_id, role_id)