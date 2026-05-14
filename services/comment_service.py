from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.comment import Comment
from schemas.comment_schema import CommentCreate, CommentUpdate
from core.logger import logger

def get_comments_by_post(post_id: int, db: Session, page: int = 1, size: int = 10):
    skip = (page - 1) * size
    comments = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.parent_id == None
    ).offset(skip).limit(size).all()
    total = db.query(Comment).filter(Comment.post_id == post_id).count()
    return {"comments": comments, "total": total, "page": page, "size": size}

def get_comment_by_id(comment_id: int, db: Session):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

def create_comment(data: CommentCreate, user_id: int, db: Session):
    comment = Comment(
        content=data.content,
        post_id=data.post_id,
        user_id=user_id,
        parent_id=data.parent_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    logger.info(f"Comment created | id={comment.id} | user_id={user_id} | post_id={data.post_id}")
    return comment

def update_comment(comment_id: int, data: CommentUpdate, current_user, db: Session):
    comment = get_comment_by_id(comment_id, db)
    if current_user.role.value != "admin" and comment.user_id != current_user.id:
        logger.warning(f"Unauthorized comment update | user_id={current_user.id} | comment_id={comment_id}")
        raise HTTPException(status_code=403, detail="Not authorized")
    comment.content = data.content
    db.commit()
    db.refresh(comment)
    logger.info(f"Comment updated | id={comment_id} | user_id={current_user.id}")
    return comment

def delete_comment(comment_id: int, current_user, db: Session):
    comment = get_comment_by_id(comment_id, db)
    if current_user.role.value != "admin" and comment.user_id != current_user.id:
        logger.warning(f"Unauthorized comment delete | user_id={current_user.id} | comment_id={comment_id}")
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(comment)
    db.commit()
    logger.info(f"Comment deleted | id={comment_id} | user_id={current_user.id}")