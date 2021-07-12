from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models

def get_user_by_id(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number {user_id} was not found!")
    return user