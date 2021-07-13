from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from . import user, userai, files

def check_access_ai_exception(user_id: int, ai_id: str, db):
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.fk_ai_id == ai_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id {user_id} has no access to AI model id {ai_id}!")
    return entry

def check_access_ai(user_id: int, ai_id: str, db):
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.fk_ai_id == ai_id).first()
    if not entry:
        return False
    return True

def check_owner(user_id: int, ai_id: str, db):
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.fk_ai_id == ai_id).with_entities(models.UserAIList.owner).first()
    if not entry:
        return {"owner": False}
    return entry

def delete(user_id: int, ai_id: str, db: Session):
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.fk_ai_id == ai_id)
    if not entry.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id: {user_id}, ai model id: {ai_id} not found in database!")
    try:
        entry.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User id: {user_id}, ai model id: {ai_id} error deleting from database!")
    return True

def user_owned_ai_list(user_id: int, db: Session):
    #check the user exists
    user.get_user_by_id(user_id, db)
    #get entries where user is the owner from UserAIList
    userai = db.query(models.UserAIList, models.AI, models.User).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.owner == True).outerjoin(models.AI).outerjoin(models.User).all()
    if not userai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User id: {user_id}, does not own AI models in the database!")
    return userai