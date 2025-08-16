from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any, Callable
from jose import jwt, JWTError
from datetime import datetime, timezone
import asyncio
from functools import wraps

from app.core.exceptions import ErrorFactory
from app.logging import logger
from app.dependencies import (
    AuthServiceDep, 
    RoleServiceDep, 
    ResourceServiceDep, 
    UserServiceDep
)

security = HTTPBearer(auto_error=False)

class AuthorizationMiddleware:
    def __init__(self):
        self._permission_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300 
        
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached data is still valid"""
        if not cached_data or 'timestamp' not in cached_data:
            return False
        
        cache_age = (datetime.now(timezone.utc) - cached_data['timestamp']).total_seconds()
        return cache_age < self._cache_ttl
    
    def _cache_permissions(self, user_id: str, permissions: Dict[str, Any]) -> None:
        """Cache user permissions"""
        self._permission_cache[user_id] = {
            'permissions': permissions,
            'timestamp': datetime.now(timezone.utc)
        }
    
    def authenticate_user(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials],
        auth_service: AuthServiceDep
    ) -> Dict[str, Any]:
        """Authenticate user and return user information"""
        if not credentials:
            raise ErrorFactory.unauthorized(
                user_message="Authentication token is required",
                context={"error": "missing_token"}
            )
        
        try:
            user_info = auth_service.verify_token(credentials.credentials)
            
            if not user_info:
                raise ErrorFactory.unauthorized(
                    user_message="Invalid or expired authentication token",
                    context={"error": "invalid_token"}
                )
            
            return user_info
            
        except jwt.ExpiredSignatureError:
            raise ErrorFactory.unauthorized(
                user_message="Authentication token has expired",
                context={"error": "expired_token"}
            )
        except JWTError as e:
            logger.error(f"JWT error: {str(e)}")
            raise ErrorFactory.unauthorized(
                user_message="Invalid authentication token",
                context={"error": "jwt_error"}
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise ErrorFactory.unauthorized(
                user_message="Authentication failed",
                context={"error": "auth_service_error"}
            )
    
    def _get_user_roles(self, user_id: str, user_service: UserServiceDep, role_service: RoleServiceDep) -> List[Dict[str, Any]]:
        """Get roles assigned to a user"""
        try:
            user = user_service.get_user_by_provider_id(provider_id=user_id)
            if not user:
                logger.warning(f"User not found for provider_id: {user_id}")
                return []
            print("User found", user.id)
            roles = role_service.get_role_by_user_id(user.id)
            print(roles)
            return roles
            
        except Exception as e:
            logger.error(f"Error getting user roles for user_id {user.id}: {str(e)}")
            return []

    def get_user_permissions(
        self, 
        user_id: str, 
        user_service: UserServiceDep,
        role_service: RoleServiceDep
    ) -> Dict[str, Any]:
        """Get user permissions with caching"""
        cached_data = self._permission_cache.get(user_id)
        if cached_data and self._is_cache_valid(cached_data):
            return cached_data['permissions']
        
        try:
            user_roles = self._get_user_roles(user_id, user_service, role_service)
            if not user_roles:
                raise ErrorFactory.forbidden(
                    user_message="You are not assigned any roles",
                )

            role_names = [role.name for role in user_roles if role.name]
            all_resources = []
            all_actions = []

            for role in user_roles:
                assigned_resources = role_service.get_assigned_resources(role.id)
                for res in assigned_resources:
                    print(res)
                    all_resources.append(res["resource"])
                    if isinstance(res.get("actions"), list):
                        all_actions.extend(res["actions"])
                    elif isinstance(res.get("actions"), str):
                        all_actions.append(res["actions"])

            all_resources = list(set(all_resources))
            all_actions = list(set(all_actions))

            permissions = {
                'roles': role_names,
                'resources': all_resources,
                'actions': all_actions
            }

            # Cache the results
            self._cache_permissions(user_id, permissions)
            
            return permissions

        except Exception as e:
            logger.error(f"Error getting user permissions for user_id {user_id}: {str(e)}")
            # Never crash — return safe default
            return {'roles': [], 'resources': [], 'actions': []}
    
    def require_authentication(self) -> Callable:
        """FastAPI dependency for authentication"""
        def _require_auth(
            auth_service: AuthServiceDep,
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        ) -> Dict[str, Any]:
            return self.authenticate_user(credentials, auth_service)
        
        return _require_auth
    
    def require_permission(self, resource: str, action: str) -> Callable:
        """FastAPI dependency for permission checking"""
        def _check_permission(
            user_service: UserServiceDep ,
            role_service: RoleServiceDep,
            user_info: Dict[str, Any] = Depends(self.require_authentication()),

        ) -> None:
            user_id = user_info.get('sub') or user_info.get('user_id')
            if not user_id:
                raise ErrorFactory.unauthorized(
                    user_message="Invalid user information",
                    context={"error": "missing_user_id"}
                )
            
            permissions = self.get_user_permissions(user_id, user_service, role_service)
            
            required_permission = f"{action}:{resource}"
            user_permissions = [
                f"{a}:{r}" 
                for a in permissions.get("actions", []) 
                for r in permissions.get("resources", [])
            ]
            
            if required_permission not in user_permissions:
                logger.warning(
                    f"Permission denied for user {user_id}: "
                    f"required {required_permission}, has {user_permissions}"
                )
                raise ErrorFactory.forbidden(
                    user_message=f"You don't have permission to {action} {resource}",
                    context={
                        "required_permission": required_permission,
                        "user_id": user_id
                    }
                )
        
        return _check_permission
    
    def require_role(self, required_roles: List[str]) -> Callable:
        """FastAPI dependency for role checking"""
        def _check_role(
            user_service: UserServiceDep,
            role_service: RoleServiceDep,
            user_info: Dict[str, Any] = Depends(self.require_authentication()),
        ) -> None:
            user_id = user_info.get('sub') or user_info.get('user_id')
            if not user_id:
                raise ErrorFactory.unauthorized(
                    user_message="Invalid user information",
                    context={"error": "missing_user_id"}
                )
            
            permissions = self.get_user_permissions(user_id, user_service, role_service)
            user_roles = permissions.get("roles", [])
            
            has_required_role = any(role in user_roles for role in required_roles)
            
            if not has_required_role:
                logger.warning(
                    f"Role access denied for user {user_id}: "
                    f"required roles {required_roles}, has roles {user_roles}"
                )
                raise ErrorFactory.forbidden(
                    user_message=f"You don't have the required role(s): {', '.join(required_roles)}",
                    context={
                        "required_roles": required_roles,
                        "user_id": user_id
                    }
                )
        
        return _check_role

    async def middleware(self, request: Request, call_next):
        """Main middleware function for global authentication"""
        public_paths = [
            "/",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/health",
            "/favicon.ico"
        ]
        
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ErrorFactory.unauthorized(
                user_message="Authentication token is required",
                context={"error": "missing_auth_header"}
            )
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            request.state.token = token
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Authorization middleware error: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            else:
                raise ErrorFactory.unauthorized(
                    user_message="Authentication failed",
                    context={"error": "middleware_error"}
                )

auth_middleware = AuthorizationMiddleware()

def require_auth() -> Callable:
    """FastAPI dependency for requiring authentication"""
    return auth_middleware.require_authentication()

def require_permission(resource: str, action: str) -> Callable:
    """FastAPI dependency for requiring specific permissions"""
    return auth_middleware.require_permission(resource, action)

def require_role(roles: List[str]) -> Callable:
    """FastAPI dependency for requiring specific roles"""
    return auth_middleware.require_role(roles)

def require_admin_role() -> Callable:
    """Require admin role for sensitive operations"""
    return auth_middleware.require_role(["admin", "super_admin"])

def require_manager_role() -> Callable:
    """Require manager role for management operations"""
    return auth_middleware.require_role(["admin", "super_admin", "manager"])

def require_user_role() -> Callable:
    """Require basic user role"""
    return auth_middleware.require_role(["user", "admin", "super_admin", "manager"])

def require_resource_management() -> Callable:
    """Require permission to manage resources"""
    return auth_middleware.require_permission("resources", "manage")

def require_role_management() -> Callable:
    """Require permission to manage roles"""
    return auth_middleware.require_permission("roles", "manage")

def require_user_management() -> Callable:
    """Require permission to manage users"""
    return auth_middleware.require_permission("users", "manage")

def require_read_permission(resource: str = "resources") -> Callable:
    """Require read permission for specified resource"""
    return auth_middleware.require_permission(resource, "read")

def require_write_permission(resource: str = "resources") -> Callable:
    """Require write permission for specified resource"""
    return auth_middleware.require_permission(resource, "write")