from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models

def get_entry_from_ids(user_id:int, ai_id:str, db):
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id)
