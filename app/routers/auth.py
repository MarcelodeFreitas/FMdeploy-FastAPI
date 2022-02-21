from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import ( OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes )
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models

router = APIRouter(
    prefix="/auth",
    tags=['Authentication with scopes (FUTURE WORK)']
)

#__________________________CONSTANTS______________________

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#__________________________PYDANTIC SCHEMAS______________________

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class User(BaseModel):
    email: str
    name: str
    is_admin: bool
    
    class Config():
        orm_mode = True

#_______________CRYPTOGRAPHY CONTEXT AND SCOPE DEFINITION____________

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={"admin": "Has access to admin privileges"},
)

#__________________________FUNCTIONS______________________

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.email == username).first()
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

#__________________________ROUTERS______________________

#generate token
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print(form_data.scopes)
    if user.is_admin:
        access_token = create_access_token(
            data={"sub": user.email, "scopes": ['admin']},
            expires_delta=access_token_expires,
        )
    else:
        access_token = create_access_token(
            data={"sub": user.email, "scopes": []},
            expires_delta=access_token_expires,
        )
    return {"access_token": access_token, "token_type": "bearer"}

#example of secure router with normal user
@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

#example of secure router with admin
@router.get("/users/me/items/")
async def read_own_items(
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    return [{"item_id": "Foo", "owner": current_user.email}]