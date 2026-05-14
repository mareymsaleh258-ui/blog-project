from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.db import get_db
from services.auth_service import login_user
from services.user_service import create_user
from schemas.auth_schema import LoginRequest, TokenResponse
from schemas.user_schema import UserCreate, UserResponse
from schemas.base import BaseResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=BaseResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(data, db)
    return BaseResponse(
        success=True,
        message="User registered successfully",
        data=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=BaseResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(data.email, data.password, db)
    return BaseResponse(
        success=True,
        message="Login successful",
        data=TokenResponse(access_token=token)
    )

@router.post("/token")
def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    token = login_user(form_data.username, form_data.password, db)
    return {"access_token": token, "token_type": "bearer"}