# app/auth/utils.py

from sqlalchemy.orm import Session
from app.db.connection import User
from passlib.context import CryptContext
from jose import jwt
import os
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_pw: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_pw, hashed_pw)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, hashed_pw: str):
    new_user = User(username=username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
