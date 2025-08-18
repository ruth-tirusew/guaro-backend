import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.adapters.user.interface import IUserRepository
from app.adapters.user.models import UserModel, UserDBSchema, UserProvider
from app.logging import logging

class UserRepository(IUserRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_user(self, user_data: UserDBSchema) -> UserModel:
        user = UserModel(**user_data.dict())
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError as e:
            logging.error(f"Failed to create user: {e}")
            self.db.rollback()
            raise ValueError("User creation failed.")
        return user

    def create_user_provider(self, user_id: str, provider_id: str) -> UserProvider:
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
            raise ValueError("User creation failed.")
        return user_provider

    def get_user_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.id == user_id,UserModel.is_deleted==False).first()

    def get_user_providers(self, user_id)->List[UserProvider]:
        return self.db.query(UserProvider) \
            .filter(UserProvider.user_id == user_id) \
            .all()

    def get_user_by_provider_id(self, provider_id: str):
         user = self.db.query(UserModel).join(
             UserProvider, UserProvider.user_id == UserModel.id
         ).filter(UserProvider.provider_id == provider_id, UserModel.is_deleted==False).first()
         return user

    def get_user_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email, UserModel.is_deleted==False).first()

    def get_user_by_phone(self, phone: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.phone == phone,UserModel.is_deleted==False).first()

    def get_all_users(self) -> List[UserModel]:
        return self.db.query(UserModel).filter(UserModel.is_deleted == False).all()

    def update_user(self, user_id: str, update_data: UserDBSchema) -> UserModel:
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User update failed due to integrity error.")
        return user

    def delete_user(self, user_id: str) -> None:
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        user.is_deleted=True
        self.db.commit()
