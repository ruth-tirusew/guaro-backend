
from jose import JWTError, jwt
import requests
from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakError, KeycloakAuthenticationError
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from app.adapters.authentication.interface import (
    AuthAdapterInterface,
    TokenResponse,
    UserInfo,
    UserCredentials,
    AuthenticationUserCreate,
    UpdateUserModel
)
from app.logging import logger

class KeycloakAdapter(AuthAdapterInterface):
    def __init__(self, server_url: str, client_id: str, client_secret: str, realm: str):
        self.server_url = server_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.realm = realm
        self.keycloak_openid = None
        self.keycloak_admin = None
        self.create_auth_client()
    
    def create_auth_client(self):
        """Initialize Keycloak OpenID and Admin clients"""
        try:
            self.keycloak_openid = KeycloakOpenID(
                server_url=self.server_url,
                client_id=self.client_id,
                client_secret_key=self.client_secret,
                realm_name=self.realm,
                verify=True
            )
          
            self.keycloak_admin = KeycloakAdmin(
                server_url=self.server_url,
                client_id=self.client_id,
                client_secret_key=self.client_secret,
                realm_name=self.realm,
                verify=True
            )
            
            logger.info(f"Keycloak client initialized for realm: {self.realm}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Keycloak client: {str(e)}")
            raise
    
    def authenticate(self, credentials: UserCredentials) -> TokenResponse:
        """Authenticate user and return tokens"""
        try:
            token = self.keycloak_openid.token(
                username=credentials.username,
                password=credentials.password
            )
            
            return TokenResponse(
                access_token=token['access_token'],
                refresh_token=token['refresh_token'],
                expires_in=token['expires_in']
            )
            
        except KeycloakAuthenticationError as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            decoded_token = self.keycloak_openid.decode_token(token)  
            return decoded_token
            
        except JWTError as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed"
            )
    
    def get_user(self, user_id: str) -> UserInfo:
        """Get user information by user ID"""
        try:
            admin_token = self.keycloak_admin.token
           
            user_data = self.keycloak_admin.get_user(user_id)
    
            user_roles = self.keycloak_admin.get_realm_roles_of_user(user_id)
            role_names = [role['name'] for role in user_roles]
            
            return UserInfo(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data.get('email'),
                first_name=user_data.get('firstName'),
                last_name=user_data.get('lastName'),
                roles=role_names
            )
            
        except KeycloakError as e:
            logger.error(f"Failed to get user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user information"
            )
    
    def signout(self, token: str) -> bool:
        """Sign out user by invalidating token"""
        try:
            decoded_token = self.verify_token(token)
            self.keycloak_openid.logout(decoded_token.get('refresh_token'))
            
            return True
            
        except Exception as e:
            logger.error(f"Signout failed: {str(e)}")
            return False
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            token = self.keycloak_openid.refresh_token(refresh_token)
            
            return TokenResponse(
                access_token=token['access_token'],
                refresh_token=token['refresh_token'],
                expires_in=token['expires_in']
            )
            
        except KeycloakError as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )

    def create_user(self, user_info: AuthenticationUserCreate) -> UserInfo:
        """
        Create a new user in Keycloak.

        Args:
            user_info (UserInfo): The user information to create.

        Returns:
            UserInfo: The created user information.
        """
        try:
            user_id = self.keycloak_admin.create_user(payload=user_info.dict())
            if not user_id:
                raise Exception("Failed to create user in Keycloak")

            user = self.keycloak_admin.get_user(user_id)
            return UserInfo(
                id=user_id,
                username=user.get("username"),
                email=user.get("email"),
                first_name=user.get("firstName"),
                last_name=user.get("lastName"),
                roles=user.get("realmRoles", [])
            )
        except KeycloakError as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        except Exception as e:
            logger.error(f"Create user error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    def update_user(self, user_info:UpdateUserModel) ->UserInfo:
        try:
            user_id = self.keycloak_admin.update_user(payload=user_info.dict(), user_id=user_info.id)
            if not user_id:
                raise Exception("Failed to update user in Keycloak")

            user = self.keycloak_admin.get_user(user_info.id)
            return UserInfo(
                id=user.get("id"),
                username=user.get("username"),
                email=user.get("email"),
                first_name=user.get("firstName"),
                last_name=user.get("lastName"),
                roles=user.get("realmRoles", [])
            )

        except KeycloakError as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        except Exception as e:
            logger.error(f"Create user error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )