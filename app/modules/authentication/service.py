from typing import Dict, Any

from app.core.exceptions import ErrorFactory
from app.adapters.authentication.interface import (
    AuthAdapterInterface, 
    UserCredentials, 
    TokenResponse, 
    UserInfo, 
    RefreshTokenRequest, 
    AuthenticationUserCreate
)
from app.modules.authentication.schemas import CreateUserModel, UpdateUserModel, PasswordResetResponse

class AuthenticationService:
    def __init__(self, adapter: AuthAdapterInterface):
        self.adapter = adapter

    def authenticate(self, credentials: UserCredentials) -> TokenResponse:
        return self.adapter.authenticate(credentials)

    def create_user(self, user: CreateUserModel) -> UserInfo:
        auth_user = AuthenticationUserCreate(
            username=user.phone,
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            enabled=True,
            credentials=[{
                "type": "password",
                "value": user.password,
                "temporary": False
            }]
        )
        return self.adapter.create_user(auth_user)

    def update_user(self, user: UpdateUserModel) -> UserInfo:
        return self.adapter.update_user(user)
        
    def get_user(self, user_id: str) -> UserInfo:
        return self.adapter.get_user(user_id)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        return self.adapter.refresh_token(refresh_token)

    def signout(self, token: str) -> bool:
        return self.adapter.signout(token)

    def verify_token(self, token: str) -> Dict[str, Any]:
        return self.adapter.verify_token(token)

    def init_reset_token(self, email: str) -> str:
        # Temporary till email adapter is integrated
        return self.adapter.init_reset_token(email)

    def reset_token(self, token: str, new_password: str)->bool:
        result = self.adapter.reset_token(token, new_password)
        if not result:
            raise ErrorFactory.bad_request("Invalid or expired reset token.")

        return True
