from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from services import user_service
from schemas.user_schema import UserCreate, UserUpdate, UserResponse
from schemas.base import BaseResponse
from dependencies.db import get_current_user, require_admin
from models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=BaseResponse)
def get_all_users(db: Session = Depends(get_db)):
    users = user_service.get_all_users(db)
    return BaseResponse(success=True, message="Users fetched", data=[UserResponse.model_validate(u) for u in users])

@router.get("/{user_id}", response_model=BaseResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user_by_id(user_id, db)
    return BaseResponse(success=True, message="User fetched", data=UserResponse.model_validate(user))

@router.put("/{user_id}", response_model=BaseResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.id != user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized")
    user = user_service.update_user(user_id, data, db)
    return BaseResponse(success=True, message="User updated", data=UserResponse.model_validate(user))

@router.delete("/{user_id}", response_model=BaseResponse)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user_service.delete_user(user_id, db)
    return BaseResponse(success=True, message="User deleted")