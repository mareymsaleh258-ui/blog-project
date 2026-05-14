from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session
from database.db import get_db
from services import comment_service
from schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse
from schemas.base import BaseResponse
from dependencies.db import get_current_user
from models.user import User

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/post/{post_id}", response_model=BaseResponse)
def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    result = comment_service.get_comments_by_post(post_id, db, page, size)
    return BaseResponse(
        success=True,
        message="Comments fetched",
        data={
            "comments": [CommentResponse.model_validate(c) for c in result["comments"]],
            "total": result["total"],
            "page": result["page"],
            "size": result["size"]
        }
    )

@router.post("/", response_model=BaseResponse)
def create_comment(
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = comment_service.create_comment(data, current_user.id, db)
    return BaseResponse(
        success=True,
        message="Comment created",
        data=CommentResponse.model_validate(comment)
    )

@router.put("/{comment_id}", response_model=BaseResponse)
def update_comment(
    comment_id: int,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = comment_service.update_comment(comment_id, data, current_user, db)
    return BaseResponse(
        success=True,
        message="Comment updated",
        data=CommentResponse.model_validate(comment)
    )

@router.delete("/{comment_id}", response_model=BaseResponse)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment_service.delete_comment(comment_id, current_user, db)
    return BaseResponse(success=True, message="Comment deleted")