
from app.adapters.authentication.interface import (
    AuthAdapterInterface,
    TokenResponse,
    UserInfo,
    UserCredentials,
    AuthenticationUserCreate,
    UpdateUserModel
)
from app.logging import logger
from typing import Dict, Any

class MockAuthAdapter(AuthAdapterInterface):
    def __init__(self):
        self._users = {
            "user1": {
                "id": "1",
                "username": "user1",
                "password": "pass1",
                "email": "user1@example.com",
                "first_name": "User",
                "last_name": "One",
                "roles": ["user"]
            }
        }
        self._tokens = {}

    def authenticate(self, credentials: UserCredentials) -> TokenResponse:
        user = self._users.get(credentials.username)
        if user and user["password"] == credentials.password:
            access_token = f"mock-access-token-{user['id']}"
            refresh_token = f"mock-refresh-token-{user['id']}"
            self._tokens[access_token] = user["id"]
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600
            )
        raise Exception("Invalid credentials")

    def get_user(self, user_id: str) -> UserInfo:
        for user in self._users.values():
            if user["id"] == user_id:
                return UserInfo(
                    id=user["id"],
                    username=user["username"],
                    email=user["email"],
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    roles=user["roles"]
                )
        raise Exception("User not found")

    def signout(self, token: str) -> bool:
        if token in self._tokens:
            del self._tokens[token]
            return True
        return False

    def create_auth_client(self):
        return self  

    def verify_token(self, token: str) -> Dict[str, Any]:
        if token in self._tokens:
            user_id = self._tokens[token]
            return {"user_id": user_id, "token": token}
        raise Exception("Invalid token") 

    def create_user(self, user_info: AuthenticationUserCreate) -> UserInfo:
        if user_info.username in self._users:
            raise Exception("User already exists")
        
        new_id = f"mock-{len(self._users) + 1}"
        user_dict = {
            "id": new_id,
            "username": user_info.username,
            "password": user_info.credentials[0].get("value"),
            "email": user_info.email,
            "first_name": user_info.firstName,
            "last_name": user_info.lastName,
        }
        self._users[user_info.username] = user_dict
        return UserInfo(
            id=new_id,
            username= user_info.username,
            email=user_info.email,
            first_name=user_info.firstName,
            last_name=user_info.lastName,
            phone = user_info.username
        )

    def update_user(self, user_info: UpdateUserModel)-> UserInfo:
        for idx, user in enumerate(self._users):
            if user.id == user_id:
                updated_user = user.copy(update=update_data.dict(exclude_unset=True))
                self._users[idx] = updated_user
                return updated_user
        raise ValueError("User not found")

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        if not refresh_token.startswith("mock-refresh-token-"):
            raise Exception("Invalid refresh token")
        user_id = refresh_token.replace("mock-refresh-token-", "")
        user = None
        for u in self._users.values():
            if u["id"] == user_id:
                user = u
                break
        if not user:
            raise Exception("Invalid refresh token")
        new_access_token = f"mock-access-token-{user['id']}"
        new_refresh_token = f"mock-refresh-token-{user['id']}"
        self._tokens[new_access_token] = user["id"]
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=3600
        )