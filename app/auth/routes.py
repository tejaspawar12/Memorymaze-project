from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db.connection import get_db
from sqlalchemy.orm import Session
from app.auth import utils
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret")
ALGORITHM = "HS256"

class UserSignup(BaseModel):
    username: str
    password: str

@router.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    if utils.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_pw = utils.hash_password(user.password)
    utils.create_user(db, user.username, hashed_pw)
    return {"message": "Signup successful ✅"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = utils.get_user_by_username(db, form_data.username)
    if not user or not utils.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials ❌")
    
    # 🔑 Include user_id in the JWT
    token = utils.create_access_token({"sub": user.username, "user_id": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# ✅ Dependency to extract current user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")

        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # 👇 Return both for full traceability
        return {"username": username, "user_id": user_id}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
