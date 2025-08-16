from abc import ABC, abstractmethod
from typing import Optional, List

from app.adapters.user.models import UserModel, UserDBSchema, UserProvider

class IUserRepository(ABC):
    @abstractmethod
    def create_user(self, user_data: UserDBSchema) -> UserModel:
        pass

    @abstractmethod
    def create_user_provider(self, user_id: str, provider_id: str) -> UserProvider:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_user_providers(self, user_id)->List[UserProvider]:
        pass
    
    @abstractmethod
    def get_user_by_provider_id(self, provider_id: str):
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_user_by_phone(self, phone: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[UserModel]:
        pass

    @abstractmethod
    def update_user(self, user_id: str, update_data: UserDBSchema) -> UserModel:
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        pass