from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.db import get_db
from services import post_service
from schemas.post_schema import PostCreate, PostUpdate, PostResponse
from schemas.base import BaseResponse
from dependencies.db import get_current_user, require_admin, require_author_or_admin
from models.user import User
from core.logger import logger
router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/", response_model=BaseResponse)
def get_all_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    result = post_service.get_all_posts(db, page, size)
    return BaseResponse(success=True, message="Posts fetched", data=result)

@router.get("/{post_id}", response_model=BaseResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post_by_id(post_id, db)
    return BaseResponse(success=True, message="Post fetched", data=post)

@router.post("/", response_model=BaseResponse)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_author_or_admin)
):
    post = post_service.create_post(data, current_user.id, db)
    return BaseResponse(
        success=True,
        message="Post created",
        data=PostResponse.model_validate(post)
    )

@router.put("/{post_id}", response_model=BaseResponse)
def update_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = post_service.update_post(post_id, data, current_user, db)
    return BaseResponse(
        success=True,
        message="Post updated",
        data=PostResponse.model_validate(post)
    )

@router.delete("/{post_id}", response_model=BaseResponse)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post_service.delete_post(post_id, current_user, db)
    return BaseResponse(success=True, message="Post deleted")