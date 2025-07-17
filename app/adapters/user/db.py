from app.adapters.user.interface import IUserRepository
from app.adapters.user.models import UserModel, UserDBSchema
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

    def get_user_by_id(self, user_id: str) -> UserModel | None:
        uuid_obj = uuid.UUID(user_id)
        return self.db.query(UserModel).filter(UserModel.id == uuid_obj).first()

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
