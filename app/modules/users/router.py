from fastapi import APIRouter, HTTPException, status, Depends
from app.modules.users.schemas import UserCreate, UserUpdate, UserRead,UserList
from app.dependencies import UserServiceDep
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, user_service: UserServiceDep):
    try:
        return user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, user_service: UserServiceDep):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/by-email/{email}", response_model=UserRead)
def get_user_by_email(email: str, user_service: UserServiceDep):
    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/", response_model=UserList)
def list_users(user_service: UserServiceDep):
    return user_service.list_users()

@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: str, user_update: UserUpdate, user_service: UserServiceDep):
    try:
        user = user_service.update_user(user_id, user_update)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, user_service: UserServiceDep):
    user_service.delete_user(user_id)
    return None
