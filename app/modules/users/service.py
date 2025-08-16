from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.modules.authentication.service import AuthenticationService
from app.modules.roles.service import RoleService
from app.adapters.user.interface import IUserRepository
from app.adapters.user.models import UserDBSchema
from app.modules.users.schemas import UserCreate, UserUpdate, UserRead, UserList
from app.core.exceptions import ErrorFactory
from app.logging import logger


class UserService:
    def __init__(
        self, 
        authentication_service: AuthenticationService, 
        user_repository: IUserRepository, 
        role_service: RoleService
    ):
        self.authentication_service = authentication_service
        self.repository = user_repository
        self.role_service = role_service

    def create_user(self, user_data: UserCreate) -> UserRead:
        """Create a new user with validation and authentication service integration"""
        try:
            # Validate phone number uniqueness
            if user_data.phone:
                existing_by_phone = self.repository.get_user_by_phone(user_data.phone)
                if existing_by_phone:
                    raise ErrorFactory.conflict(
                        user_message="A user with this phone number already exists.",
                        context={"phone": user_data.phone}
                    )

            # Validate email uniqueness
            if user_data.email:
                existing_by_email = self.repository.get_user_by_email(user_data.email)
                if existing_by_email:
                    raise ErrorFactory.conflict(
                        user_message="A user with this email already exists.",
                        context={"email": user_data.email}
                    )

            # Create user in authentication service first
            auth_user = self.authentication_service.create_user(user_data)
            
            # Create user in local database
            user = self.repository.create_user(
                UserDBSchema(
                    email=user_data.email,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    phone=user_data.phone,
                )
            )
            
            # Link local user with authentication provider
            self.repository.create_user_provider(
                user_id=user.id, 
                provider_id=auth_user.id
            )
            
            # Convert UUID to string if necessary
            if hasattr(user, 'id') and isinstance(user.id, uuid.UUID):
                user.id = str(user.id)
                
            logger.info(f"User created successfully: {user.id}")
            return UserRead.from_orm(user)
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            # Rollback auth user creation if local user creation fails
            if 'auth_user' in locals():
                try:
                    self.authentication_service.delete_user(auth_user.id)
                except Exception as rollback_error:
                    logger.error(f"Failed to rollback auth user creation: {str(rollback_error)}")
            raise

    def get_user(self, user_id: uuid.UUID) -> Optional[UserRead]:
        """Get user by ID"""
        try:
            print(user_id, "__________________")
            user = self.repository.get_user_by_id(user_id)
            print("USER HERE", user)
            return UserRead.from_orm(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            raise ErrorFactory.internal_server_error(
                user_message="Failed to retrieve user",
                context={"user_id": user_id}
            )

    def get_user_by_provider_id(self, provider_id: str):
        """Get user by authentication provider ID"""
        try:
            return self.repository.get_user_by_provider_id(provider_id=provider_id)
        except Exception as e:
            logger.error(f"Error getting user by provider ID {provider_id}: {str(e)}")
            raise ErrorFactory.internal_server_error(
                user_message="Failed to retrieve user",
                context={"provider_id": provider_id}
            )

    def get_user_by_email(self, email: str) -> Optional[UserRead]:
        """Get user by email address"""
        try:
            user = self.repository.get_user_by_email(email)
            return UserRead.from_orm(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            raise ErrorFactory.internal_server_error(
                user_message="Failed to retrieve user",
                context={"email": email}
            )

    def list_users(self, limit: Optional[int] = None, offset: Optional[int] = None) -> UserList:
        """List all users with optional pagination"""
        try:
            users = self.repository.get_all_users()
            return UserList(
                users=[UserRead.from_orm(user) for user in users]
            )
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            raise ErrorFactory.internal_server_error(
                user_message="Failed to retrieve users list"
            )

    def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[UserRead]:
        """Update user information with validation"""
        try:
            # Validate email uniqueness if email is being updated
            if update_data.email:
                existing_user = self.repository.get_user_by_email(update_data.email)
                if existing_user and str(existing_user.id) != user_id:
                    raise ErrorFactory.conflict(
                        user_message="A user with this email already exists.",
                        context={"email": update_data.email, "existing_user_id": str(existing_user.id)}
                    )

            # Validate phone uniqueness if phone is being updated
            if update_data.phone:
                existing_user = self.repository.get_user_by_phone(update_data.phone)
                if existing_user and str(existing_user.id) != user_id:
                    raise ErrorFactory.conflict(
                        user_message="A user with this phone number already exists.",
                        context={"phone": update_data.phone, "existing_user_id": str(existing_user.id)}
                    )

            # Update user in repository
            user = self.repository.update_user(user_id, update_data)
            
            if user:
                logger.info(f"User updated successfully: {user_id}")
                return UserRead.from_orm(user)
            else:
                raise ErrorFactory.not_found(
                    user_message="User not found",
                    context={"user_id": user_id}
                )
                
        except Exception as e:
            if not isinstance(e, type(ErrorFactory.not_found("", {}))):
                logger.error(f"Error updating user {user_id}: {str(e)}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """Delete user and clean up related data"""
        try:
            user = self.repository.get_user_by_id(user_id)
            if not user:
                raise ErrorFactory.not_found(
                    user_message="User not found",
                    context={"user_id": user_id}
                )
            try:
                user_roles = self.role_service.get_role_by_user_id(user.id)
                for role in user_roles:
                    self.unassign_user_role(user.id, role.id)
            except Exception as role_cleanup_error:
                logger.warning(f"Failed to cleanup roles for user {user_id}: {str(role_cleanup_error)}")


            self.repository.delete_user(user_id)
            
            # TODO: Consider deleting from authentication service as well
            # self.authentication_service.delete_user(provider_id)
            
            logger.info(f"User deleted successfully: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise

    def assign_user_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Assign a role to a user"""
        try:
            # Validate user exists
            user = self.repository.get_user_by_id(user_id)
            if not user:
                raise ErrorFactory.not_found(
                    user_message="User not found",
                    context={"user_id": str(user_id)}
                )

            # Validate role exists
            role = self.role_service.get_role_by_id(str(role_id))
            if not role:
                raise ErrorFactory.not_found(
                    user_message="Role not found",
                    context={"role_id": str(role_id)}
                )

            # Check if user already has this role
            existing_roles = self.role_service.get_role_by_user_id(user.id)
            if any(str(existing_role.id) == str(role_id) for existing_role in existing_roles):
                raise ErrorFactory.conflict(
                    user_message="User already has this role assigned",
                    resource="UserRole",
                    context={"user_id": str(user_id), "role_id": str(role_id)}
                )

            # Assign the role
            success = self.repository.assign_role_to_user(user_id=user.id, role_id=role_id)
            
            if success:
                logger.info(f"Role {role_id} assigned to user {user_id}")
                return True
            else:
                raise ErrorFactory.internal_error(
                    user_message="Failed to assign role to user",
                    context={"user_id": str(user_id), "role_id": str(role_id)}
                )
                
        except Exception as e:
            logger.error(f"Error assigning role {role_id} to user {user_id}: {str(e)}")
            raise

    def unassign_user_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Remove a role assignment from a user"""
        try:
            # Validate user exists
            user = self.repository.get_user_by_id(str(user_id))
            if not user:
                raise ErrorFactory.not_found(
                    user_message="User not found",
                    context={"user_id": str(user_id)}
                )

            # Check if user has this role
            existing_roles = self.role_service.get_role_by_user_id(user.id)
            if not any(str(existing_role.id) == str(role_id) for existing_role in existing_roles):
                raise ErrorFactory.not_found(
                    user_message="User does not have this role assigned",
                    context={"user_id": str(user_id), "role_id": str(role_id)}
                )

            # Unassign the role
            success = self.role_service.unassign_role_from_user(user_id=user.id, role_id=role_id)
            
            if success:
                logger.info(f"Role {role_id} unassigned from user {user_id}")
                return True
            else:
                raise ErrorFactory.internal_server_error(
                    user_message="Failed to unassign role from user",
                    context={"user_id": str(user_id), "role_id": str(role_id)}
                )
                
        except Exception as e:
            logger.error(f"Error unassigning role {role_id} from user {user_id}: {str(e)}")
            raise

    def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all roles assigned to a user"""
        try:
            user = self.repository.get_user_by_id(user_id)
            if not user:
                raise ErrorFactory.not_found(
                    user_message="User not found",
                    context={"user_id": user_id}
                )

            roles = self.role_service.get_role_by_user_id(user.id)
            return roles if roles else []
            
        except Exception as e:
            logger.error(f"Error getting roles for user {user_id}: {str(e)}")
            raise

    # def get_users_by_role(self, role_id: str) -> List[UserRead]:
    #     """Get all users assigned to a specific role"""
    #     try:
    #         # Validate role exists
    #         role = self.role_service.get_role_by_id(role_id)
    #         if not role:
    #             raise ErrorFactory.not_found(
    #                 user_message="Role not found",
    #                 context={"role_id": role_id}
    #             )

    #         users = self.repository.get_users_by_role_id(role_id)
    #         return [UserRead.from_orm(user) for user in users]
            
    #     except Exception as e:
    #         logger.error(f"Error getting users for role {role_id}: {str(e)}")
    #         raise
