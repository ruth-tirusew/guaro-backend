from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from pydantic import BaseModel


class UserCredentials(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UpdateUserModel(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserInfo(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AuthenticationCredential(BaseModel):
    type: str = "password"
    value: str
    temporary: bool = False

class AuthenticationUserCreate(BaseModel):
    username: str
    email: str = None
    firstName: str
    lastName: str
    enabled: bool = True
    credentials: list

class AuthAdapterInterface(ABC):
    @abstractmethod
    def authenticate(self, credentials):
        """Authenticate a user with the provided credentials."""
        pass

    @abstractmethod
    def get_user(self, user_id):
        """Retrieve user information by user_id."""
        pass

    @abstractmethod
    def signout(self, token):
        """Sign out a user by invalidating their token or session."""
        pass

    @abstractmethod
    def create_auth_client(self):
        """Create and return an underlying auth client instance"""
        pass

    @abstractmethod
    def verify_token(self, token):
        """Verify the validity of an authentication token."""
        pass 

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        pass

    @abstractmethod
    def create_user(self, user_info: UserInfo, password: str) -> UserInfo:
        """
        Create a new user in the authentication provider.

        Args:
            user_info (UserInfo): The user information to create.
            password (str): The password for the new user.

        Returns:
            UserInfo: The created user information.
        """
        pass

    @abstractmethod
    def update_user(self, user:UpdateUserModel)->UserInfo:
        pass


    @abstractmethod
    def init_reset_token(self, email: str)->str:
        pass

    @abstractmethod
    def reset_token(self, token: str)->bool:
        pass



    