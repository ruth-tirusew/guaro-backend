from app.adapters.user.interface import IUserRepository
from app.adapters.user.models import UserModel, UserDBSchema, UserProvider

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

class UserRepository(IUserRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_user(self, user_data: UserDBSchema) -> UserModel:
        user = UserModel(**user_data.dict())
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed.")
        return user

    def create_user_proviider(self, user_id: str, provider_id: str) -> UserProvider:
        user_provider=UserProvider(
            user_id = user_id,
            provider_id = provider_id
        )
        self.db.add(user_provider)
        try:
            self.db.commit()
            self.db.refresh(user_provider)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed.")
        return user_provider

    def get_user_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_user_by_provider_id(self, provider_id: str):
        print(provider_id)
        user = self.db.query(UserModel).join(
            UserProvider, UserProvider.user_id == UserModel.id
        ).filter(UserProvider.provider_id == provider_id).first()
        print("User provider")
        print(user)
        return user

    def get_user_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_user_by_phone(self, phone: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.phone == phone).first()

    def get_all_users(self) -> list[UserModel]:
        return self.db.query(UserModel).all()

    def update_user(self, user_id: str, update_data: UserDBSchema) -> UserModel:
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User update failed due to integrity error.")
        return user

    def delete_user(self, user_id: str) -> None:
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        self.db.delete(user)
        self.db.commit()
