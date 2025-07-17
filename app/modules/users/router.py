from fastapi import APIRouter, HTTPException, status
from app.container import get_container
from app.modules.users.schemas import UserCreate, UserUpdate, UserRead,UserList

router = APIRouter(prefix="/users", tags=["Users"])

container = get_container()
user_service = container.resolve("user_service")

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    try:
        return user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/by-email/{email}", response_model=UserRead)
def get_user_by_email(email: str):
    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/", response_model=UserList)
def list_users():
    return user_service.list_users()

@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: str, user_update: UserUpdate):
    try:
        user = user_service.update_user(user_id, user_update)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    user_service.delete_user(user_id)
    return None
