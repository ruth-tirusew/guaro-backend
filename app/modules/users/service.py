from app.dependencies import get_auth_adapter
from app.adapters.authentication.interface import UserCredentials, TokenResponse, UserInfo, RefreshTokenRequest
from typing import Dict, Any

class AuthService:
    def __init__(self):
        self.adapter = get_auth_adapter()

    def authenticate(self, credentials: UserCredentials) -> TokenResponse:
        return self.adapter.authenticate(credentials)

    def get_user(self, user_id: str) -> UserInfo:
        return self.adapter.get_user(user_id)

    def signout(self, token: str) -> bool:
        return self.adapter.signout(token)

    def verify_token(self, token: str) -> Dict[str, Any]:
        return self.adapter.verify_token(token)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        if hasattr(self.adapter, 'refresh_token'):
            return self.adapter.refresh_token(refresh_token)
        raise NotImplementedError('refresh_token not implemented in this adapter')
