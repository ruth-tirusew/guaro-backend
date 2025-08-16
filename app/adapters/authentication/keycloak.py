import json
from jose import JWTError, jwt
import requests
from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakError, KeycloakAuthenticationError
from typing import Dict, Any

from app.adapters.authentication.interface import (
    AuthAdapterInterface,
    TokenResponse,
    UserInfo,
    UserCredentials,
    AuthenticationUserCreate,
    UpdateUserModel
)
from app.adapters.authentication.errors import (
    AuthenticationError,
    AuthenticationAdapterError,
    InvalidCredentialsError,
    ExternalServiceUnavailableError,
    TokenRefreshError,
    TokenVerificationError,
    UserCreationError,
    UserNotFoundError,
    UserUpdateError,

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
        self._initialize_clients()
    
    def _initialize_clients(self):
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
            raise ExternalServiceUnavailableError(
                "Failed to initialize Keycloak connection", 
                original_error=e
            )
    
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
            logger.error(f"Authentication failed for user {credentials.username}: {str(e)}")
            raise InvalidCredentialsError(
                f"Authentication failed for user {credentials.username}",
                original_error=e
            )
        except KeycloakError as e:
            logger.error(f"Keycloak error during authentication: {str(e)}")
            raise ExternalServiceUnavailableError(
                "Authentication service is temporarily unavailable",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}")
            raise ExternalServiceUnavailableError(
                "Authentication service encountered an unexpected error",
                original_error=e
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            decoded_token = self.keycloak_openid.decode_token(token)  
            return decoded_token
            
        except JWTError as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise TokenVerificationError(
                "Invalid or expired token",
                original_error=e
            )
        except KeycloakError as e:
            logger.error(f"Keycloak error during token verification: {str(e)}")
            raise ExternalServiceUnavailableError(
                "Token verification service is temporarily unavailable",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Unexpected token verification error: {str(e)}")
            raise TokenVerificationError(
                "Token verification failed due to unexpected error",
                original_error=e
            )
    
    def get_user(self, user_id: str) -> UserInfo:
        """Get user information by user ID"""
        try:           
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
            if "404" in str(e) or "not found" in str(e).lower():
                logger.error(f"User not found: {user_id}")
                raise UserNotFoundError(f"User with ID {user_id} not found", original_error=e)
            else:
                logger.error(f"Keycloak error while getting user {user_id}: {str(e)}")
                raise ExternalServiceUnavailableError(
                    "User service is temporarily unavailable",
                    original_error=e
                )
        except Exception as e:
            logger.error(f"Unexpected error while getting user {user_id}: {str(e)}")
            raise ExternalServiceUnavailableError(
                "Failed to retrieve user information due to unexpected error",
                original_error=e
            )
    
    def signout(self, token: str) -> bool:
        """Sign out user by invalidating token"""
        try:
            decoded_token = self.verify_token(token)
            refresh_token = decoded_token.get('refresh_token')
            
            if refresh_token:
                self.keycloak_openid.logout(refresh_token)
            
            return True
            
        except (TokenVerificationError, ExternalServiceUnavailableError):
            logger.warning("Attempted to logout with invalid token")
            return True
        except Exception as e:
            logger.error(f"Unexpected error during signout: {str(e)}")
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
            
        except KeycloakAuthenticationError as e:
            logger.error(f"Token refresh failed - invalid refresh token: {str(e)}")
            raise TokenRefreshError(
                "Invalid or expired refresh token",
                original_error=e
            )
        except KeycloakError as e:
            logger.error(f"Keycloak error during token refresh: {str(e)}")
            raise ExternalServiceUnavailableError(
                "Token refresh service is temporarily unavailable",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Unexpected token refresh error: {str(e)}")
            raise TokenRefreshError(
                "Token refresh failed due to unexpected error",
                original_error=e
            )

    def create_user(self, user_info: AuthenticationUserCreate) -> UserInfo:
        """Create a new user in Keycloak"""
        try:
            user_payload = user_info.dict()
            user_id = self.keycloak_admin.create_user(payload=user_payload)
            
            if not user_id:
                raise UserCreationError(
                    "Keycloak returned empty user ID after creation",
                    user_data={"username": user_info.username, "email": user_info.email}
                )

            # Get the created user data
            user_data = self.keycloak_admin.get_user(user_id)
            
            return UserInfo(
                id=user_id,
                username=user_data.get("username"),
                email=user_data.get("email"),
                first_name=user_data.get("firstName"),
                last_name=user_data.get("lastName"),
                roles=user_data.get("realmRoles", [])
            )
            
        except KeycloakError as e:
            error_msg = str(e).lower()
            user_context = {"username": user_info.username, "email": user_info.email}
            
            if "exists" in error_msg or "conflict" in error_msg:
                logger.error(f"User creation failed - user already exists: {user_info.username}")
                decoded_error_message = e.error_message.decode('utf-8') 
                raise UserCreationError(
                    json.loads(decoded_error_message).get("errorMessage"),
                    user_data=user_context,
                    original_error=e
                )
            elif "invalid" in error_msg or "bad request" in error_msg:
                logger.error(f"User creation failed - invalid user data: {str(e)}")
                raise UserCreationError(
                    "Invalid user data provided",
                    user_data=user_context,
                    original_error=e
                )
            else:
                logger.error(f"Keycloak error during user creation: {str(e)}")
                raise ExternalServiceUnavailableError(
                    "User creation service is temporarily unavailable",
                    original_error=e
                )
        except Exception as e:
            if isinstance(e, UserCreationError):
                raise
            logger.error(f"Unexpected error during user creation: {str(e)}")
            raise UserCreationError(
                "User creation failed due to unexpected error",
                user_data={"username": user_info.username, "email": user_info.email},
                original_error=e
            )
    def delete_user(self, user_id)-> None:
        try:
            self.keycloak_admin.delete_user(user_id=user_id)
        except KeycloakError as e:
            error_msg = str(e).lower()
            
            if "404" in error_msg or "not found" in error_msg:
                logger.error(f"User update failed - user not found: {user_info.id}")
                raise UserNotFoundError(
                    f"User with ID {user_info.id} not found",
                    original_error=e
                )  

        except Exception as e:
            if isinstance(e, (UserNotFoundError, UserUpdateError)):
                raise
            logger.error(f"Unexpected error during user delete: {str(e)}")
            raise UserUpdateError(
                "User delete failed due to unexpected error",
                user_id=user_info.id,
                original_error=e
            )
    def update_user(self, user_info: UpdateUserModel) -> UserInfo:
        """Update user information in Keycloak"""
        try:
            self.keycloak_admin.update_user(
                user_id=user_info.id, 
                payload=user_info.dict(exclude={'id'})
            )
            
            # Get the updated user data
            user_data = self.keycloak_admin.get_user(user_info.id)
            
            return UserInfo(
                id=user_data.get("id"),
                username=user_data.get("username"),
                email=user_data.get("email"),
                first_name=user_data.get("firstName"),
                last_name=user_data.get("lastName"),
                roles=user_data.get("realmRoles", [])
            )

        except KeycloakError as e:
            error_msg = str(e).lower()
            
            if "404" in error_msg or "not found" in error_msg:
                logger.error(f"User update failed - user not found: {user_info.id}")
                raise UserNotFoundError(
                    f"User with ID {user_info.id} not found",
                    original_error=e
                )
            elif "invalid" in error_msg or "bad request" in error_msg:
                logger.error(f"User update failed - invalid user data: {str(e)}")
                raise UserUpdateError(
                    "Invalid user data provided for update",
                    user_id=user_info.id,
                    original_error=e
                )
            else:
                logger.error(f"Keycloak error during user update: {str(e)}")
                raise ExternalServiceUnavailableError(
                    "User update service is temporarily unavailable",
                    original_error=e
                )
        except Exception as e:
            if isinstance(e, (UserNotFoundError, UserUpdateError)):
                raise
            logger.error(f"Unexpected error during user update: {str(e)}")
            raise UserUpdateError(
                "User update failed due to unexpected error",
                user_id=user_info.id,
                original_error=e
            )
