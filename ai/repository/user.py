from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, hashing

def get_user_by_id(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number {user_id} was not found!")
    return user

def create_user(name: str, email: str, password: str, db: Session):
    new_user = models.User(name=name, email=email, password=hashing.Hash.bcrypt(password))
    try: 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
        detail=f"Email: {email}, is already registered!")
    return new_user

def get_all_users(db: Session):
    user_list = db.query(models.User).all()
    if not user_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"No users found in database!")
    return user_list