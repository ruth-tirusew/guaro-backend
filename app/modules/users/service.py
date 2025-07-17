from app.modules.authentication.service import AuthenticationService
from app.adapters.user.interface import IUserRepository
from app.modules.users.schemas import UserCreate, UserUpdate, UserRead

from typing import List, Optional

class UserService:
    def __init__(self, authentication_service: AuthenticationService, user_repository: IUserRepository):
        self.authentication_service = authentication_service
        self.repository = user_repository

    def create_user(self, user_data: UserCreate) -> UserRead:
        if user_data.phone:
            existing_by_phone = self.repository.get_user_by_phone(user_data.phone)
            if existing_by_phone:
                raise ValueError("A user with this phone number already exists.")

        if user_data.email:
            existing_by_email = self.repository.get_user_by_email(user_data.email)
            if existing_by_email:
                raise ValueError("A user with this email already exists.")
        
        auth_user = self.authentication_service.create_user(user_data)
        user = self.repository.create_user(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            external_id=auth_user.id,
            phone=getattr(user_data, "phone", None),
            username=getattr(user_data, "username", None)
        )
        return UserRead.from_orm(user)

    def get_user(self, user_id: str) -> Optional[UserRead]:
        user = self.repository.get_user_by_id(user_id)
        return UserRead.from_orm(user) if user else None

    def get_user_by_email(self, email: str) -> Optional[UserRead]:
        user = self.repository.get_user_by_email(email)
        return UserRead.from_orm(user) if user else None

    def list_users(self) -> List[UserRead]:
        users = self.repository.get_all_users()
        return [UserRead.from_orm(user) for user in users]

    def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[UserRead]:
        email = update_data.email
        if email:
            existing_user = self.repository.get_user_by_email(email)
            if existing_user and str(existing_user.id) != user_id:
                raise ValueError("A user with this email already exists.")

        phone = update_data.phone
        if phone:
            existing_user = self.repository.get_user_by_phone(phone)
            if existing_user and str(existing_user.id) != user_id:
                raise ValueError("A user with this phone number already exists.")

        user = self.repository.update_user(user_id, update_data)
        return UserRead.from_orm(user) if user else None

    def delete_user(self, user_id: str) -> bool:
        self.repository.delete_user(user_id)
        return True