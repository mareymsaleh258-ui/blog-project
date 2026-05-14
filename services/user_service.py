from sqlalchemy.orm import Session
from models.user import User
from schemas.user_schema import UserCreate, UserUpdate
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def create_user(data: UserCreate, db: Session):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(user_id: int, data: UserUpdate, db: Session):
    user = get_user_by_id(user_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(user_id: int, db: Session):
    user = get_user_by_id(user_id, db)
    db.delete(user)
    db.commit()