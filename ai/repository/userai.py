from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models

def check_access_ai_exception(user_id:int, ai_id:str, db):
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.fk_ai_id == ai_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id {user_id} has no access to AI model id {ai_id}!")
    return entry

def check_access_ai(user_id:int, ai_id:str, db):
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.fk_ai_id == ai_id).first()
    if not entry:
        return False
    return True