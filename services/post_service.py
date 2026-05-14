from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.post import Post
from schemas.post_schema import PostCreate, PostUpdate, PostResponse
from core.redis_client import redis_client
import json
from core.logger import logger

CACHE_EXPIRE = 300

def get_all_posts(db: Session, page: int = 1, size: int = 10):
    cache_key = f"posts:page:{page}:size:{size}"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except:
        pass

    skip = (page - 1) * size
    posts = db.query(Post).offset(skip).limit(size).all()
    total = db.query(Post).count()
    result = {
        "posts": [PostResponse.model_validate(p).model_dump(mode="json") for p in posts],
        "total": total,
        "page": page,
        "size": size
    }
    try:
        redis_client.setex(cache_key, CACHE_EXPIRE, json.dumps(result))
    except:
        pass
    return result

def get_post_by_id(post_id: int, db: Session):
    cache_key = f"post:{post_id}"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except:
        pass

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    result = PostResponse.model_validate(post).model_dump(mode="json")
    try:
        redis_client.setex(cache_key, CACHE_EXPIRE, json.dumps(result))
    except:
        pass
    return result

def invalidate_cache(post_id: int = None):
    try:
        keys = redis_client.keys("posts:*")
        if keys:
            redis_client.delete(*keys)
        if post_id:
            redis_client.delete(f"post:{post_id}")
    except:
        pass

def create_post(data: PostCreate, author_id: int, db: Session):
    post = Post(title=data.title, content=data.content, author_id=author_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    invalidate_cache()
    logger.info(f"Post created | id={post.id} | author_id={author_id}")
    return post

def update_post(post_id: int, data: PostUpdate, current_user, db: Session):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if current_user.role.value != "admin" and post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    invalidate_cache(post_id)
    logger.info(f"Post updated | id={post_id} | user_id={current_user.id}")
    return post

def delete_post(post_id: int, current_user, db: Session):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if current_user.role.value != "admin" and post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(post)
    db.commit()
    invalidate_cache(post_id)
    logger.info(f"Post deleted | id={post_id} | user_id={current_user.id}")