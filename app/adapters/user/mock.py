from app.adapters.user.interface import IUserRepository
from app.modules.users.schemas import UserCreate, UserRead
from typing import Optional, List
import uuid

class MockUserRepository(IUserRepository):
    def __init__(self):
        self.users = [] 

    def create_user(self, user_data: UserCreate) -> UserRead:
        user_id = str(uuid.uuid4())
        user = UserRead(id=user_id, **user_data.dict())
        self.users.append(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[UserRead]:
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[UserRead]:
        for user in self.users:
            if user.email == email:
                return user
        return None

    def get_user_by_phone(self, phone: str) -> Optional[UserRead]:
        for user in self.users:
            if user.phone == phone:
                return user
        return None

    def get_all_users(self) -> List[UserRead]:
        return list(self.users)

    def update_user(self, user_id: str, update_data: UserCreate) -> UserRead:
        for idx, user in enumerate(self.users):
            if user.id == user_id:
                updated_user = user.copy(update=update_data.dict(exclude_unset=True))
                self.users[idx] = updated_user
                return updated_user
        raise ValueError("User not found")

    def delete_user(self, user_id: str) -> None:
        self.users = [user for user in self.users if user.id != user_id]
