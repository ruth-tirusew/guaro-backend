from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.adapters.role.interface import IRoleRepository
from app.adapters.role.models import Role, RoleDBSchema, RoleCreate, RoleResource, UserRole
from app.adapters.resource.models import Resource 
from typing import List, Optional
from uuid import UUID

from app.logging import logger


class RoleRepository(IRoleRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role_data: RoleCreate) -> RoleDBSchema:
        """Create a new role"""
        db_role = Role(**role_data.model_dump())
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return RoleDBSchema.model_validate(db_role)

    def get_role_by_id(self, role_id: str) -> Optional[RoleDBSchema]:
        """Get role by ID"""
        try:
            uuid_obj = UUID(role_id)
            db_role = self.db.query(Role).filter(Role.id == uuid_obj).first()
            if db_role:
                return RoleDBSchema.model_validate(db_role)
            return None
        except ValueError:
            return None

    def get_role_by_user_id(self, user_id: UUID) -> List[RoleDBSchema]:
        """Get all roles assigned to a user - FIXED VERSION"""
        try:
            roles = (
                self.db.query(Role)
                .join(UserRole, Role.id == UserRole.role_id)
                .filter(
                    UserRole.user_id == user_id,
                    UserRole.is_deleted == False 
                )
                .all()
            )
            return [RoleDBSchema.model_validate(role) for role in roles]
        except Exception as e:
            logger.error(f"Error in get_role_by_user_id: {str(e)}")
            return []

    def get_role_by_name(self, name: str) -> Optional[RoleDBSchema]:
        """Get role by name"""
        db_role = self.db.query(Role).filter(Role.name == name).first()
        if db_role:
            return RoleDBSchema.model_validate(db_role)
        return None

    def get_all_roles(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[RoleDBSchema]:
        """Get all roles with optional pagination"""
        query = self.db.query(Role).filter(Role.is_deleted == False)
        
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
            
        db_roles = query.all()
        return [RoleDBSchema.model_validate(role) for role in db_roles]

    def update_role(self, role_id: str, update_data: RoleCreate) -> Optional[RoleDBSchema]:
        """Update role information"""
        try:
            uuid_obj = UUID(role_id)
            db_role = self.db.query(Role).filter(Role.id == uuid_obj).first()
            
            if not db_role:
                return None
                
            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(db_role, key, value)
                
            self.db.commit()
            self.db.refresh(db_role)
            return RoleDBSchema.model_validate(db_role)
            
        except ValueError:
            # Invalid UUID format
            return None

    def delete_role(self, role_id: str) -> bool:
        """Soft delete a role"""
        try:
            uuid_obj = UUID(role_id)
            db_role = self.db.query(Role).filter(Role.id == uuid_obj).first()
            
            if db_role:
                # Soft delete - mark as deleted instead of removing
                db_role.is_deleted = True
                self.db.commit()
                return True
            return False
            
        except ValueError:
            # Invalid UUID format
            return False

    def assign_role_to_resource(self, resource_id: str, role_id: str) -> bool:
        """Assign a role to a resource"""
        try:
            role_uuid = UUID(role_id)
            resource_uuid = UUID(resource_id)
            
            # Check if assignment already exists
            existing = self.db.query(RoleResource).filter_by(
                role_id=role_uuid, 
                resource_id=resource_uuid,
                is_deleted=False
            ).first()
            
            if not existing:
                db_role_resource = RoleResource(
                    role_id=role_uuid, 
                    resource_id=resource_uuid
                )
                self.db.add(db_role_resource)
                self.db.commit()
                return True
            return False 
            
        except ValueError:
            return False

    def unassign_role_from_resource(self, resource_id: str, role_id: str) -> bool:
        """Remove role assignment from a resource"""
        try:
            role_uuid = UUID(role_id)
            resource_uuid = UUID(resource_id)
            
            db_role_resource = self.db.query(RoleResource).filter_by(
                role_id=role_uuid, 
                resource_id=resource_uuid,
                is_deleted=False
            ).first()
            
            if db_role_resource:
                db_role_resource.is_deleted = True
                self.db.commit()
                return True
            return False  # Assignment not found
            
        except ValueError:
            # Invalid UUID format
            return False

    def get_assigned_resources(self, role_id: UUID) -> List[dict]:
        """Get all resources assigned to a role"""
        try:
            resources = (
                self.db.query(Resource)
                .join(RoleResource, Resource.id == RoleResource.resource_id)
                .filter(
                    RoleResource.role_id == role_id,
                    RoleResource.is_deleted == False,
                    Resource.is_deleted == False
                )
                .all()
            )
            return [
                {
                    "id": str(resource.id),
                    "name": resource.name,
                    "resource":resource.resource,
                    "actions": resource.action
                }
                for resource in resources
            ]
            
        except ValueError:
            # Invalid UUID format
            return []

    def assign_user_role(self, user_id: UUID, role_id: UUID) -> bool:
        """Assign a role to a user"""
        try:
            # Check if assignment already exists
            existing = self.db.query(UserRole).filter_by(
                role_id=role_id, 
                user_id=user_id,
                is_deleted=False
            ).first()
            
            if not existing:
                # Check if there's a previously deleted assignment to reactivate
                deleted_assignment = self.db.query(UserRole).filter_by(
                    role_id=role_id, 
                    user_id=user_id,
                    is_deleted=True
                ).first()
                
                if deleted_assignment:
                    # Reactivate the assignment
                    deleted_assignment.is_deleted = False
                else:
                    # Create new assignment
                    db_user_role = UserRole(role_id=role_id, user_id=user_id)
                    self.db.add(db_user_role)
                    
                self.db.commit()
                return True
                
            return False  # Already assigned
            
        except Exception as e:
            logger.error(f"Error in assign_user_role: {str(e)}")
            self.db.rollback()
            return False

    def unassign_user_role(self, user_id: UUID, role_id: UUID) -> bool:
        """Remove role assignment from a user"""
        try:
            existing = self.db.query(UserRole).filter_by(
                role_id=role_id, 
                user_id=user_id,
                is_deleted=False
            ).first()
            
            if existing:
                existing.is_deleted = True
                self.db.commit()
                return True
                
            return False 
            
        except Exception as e:
            logger.error(f"Error in unassign_user_role: {str(e)}")
            self.db.rollback()
            return False

    def get_users_by_role_id(self, role_id: str) -> List[dict]:
        """Get all users assigned to a specific role"""
        try:
            uuid_obj = UUID(role_id)
            from app.adapters.user.models import User 
            
            users = (
                self.db.query(User)
                .join(UserRole, User.id == UserRole.user_id)
                .filter(
                    UserRole.role_id == uuid_obj,
                    UserRole.is_deleted == False,
                    User.is_deleted == False 
                )
                .all()
            )
            
            return [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone
                }
                for user in users
            ]
            
        except ValueError:
            # Invalid UUID format
            return []

    def search_roles(self, query: str, limit: Optional[int] = 10) -> List[RoleDBSchema]:
        """Search roles by name or description"""
        db_roles = (
            self.db.query(Role)
            .filter(
                Role.is_deleted == False,
                (Role.name.ilike(f"%{query}%") | Role.description.ilike(f"%{query}%"))
            )
            .limit(limit)
            .all()
        )
        return [RoleDBSchema.model_validate(role) for role in db_roles]

    def count_roles(self) -> int:
        return self.db.query(Role).filter(Role.is_deleted == False).count()

    def get_role_permissions(self, role_id: str) -> dict:
        try:
            uuid_obj = UUID(role_id)
            
            # Get role information
            role = self.db.query(Role).filter(Role.id == uuid_obj).first()
            if not role:
                return {"role": None, "resources": [], "actions": []}
            
            # Get assigned resources with their actions
            resources = self.get_assigned_resources(role_id)
            
            # Extract unique actions from all resources
            all_actions = set()
            resource_names = []
            
            for resource in resources:
                resource_names.append(resource["name"])
                if resource.get("actions"):
                    all_actions.update(resource["actions"])
            
            return {
                "role": {
                    "id": str(role.id),
                    "name": role.name,
                },
                "resources": resource_names,
                "actions": list(all_actions)
            }
            
        except ValueError:
            return {"role": None, "resources": [], "actions": []}


            