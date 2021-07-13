from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .. import schemas, models
from . import user, userai, files, ai

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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User id: {user_id}, ai model id: {ai_id} is not the owner!")
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

def user_share_ai(user_id_sharer: int, user_id_beneficiary: int, ai_id: str, db: Session):
    #check if user is the owner
    check_owner(user_id_sharer, ai_id, db)
    #check the user exists
    user.get_user_by_id(user_id_sharer, db)
    #check user beneficiary exists
    user.get_user_by_id(user_id_beneficiary, db)
    #check the ai model exists
    ai.get_ai_by_id(ai_id, db)
    #check if it is already shared with this user
    check_shared(user_id_beneficiary, ai_id, db)
    #create UserAi List table entry where owner=false and beneficiary=true
    new_ai_user_list = models.UserAIList(fk_user_id=user_id_beneficiary, fk_ai_id=ai_id,owner=False, beneficiary=True)
    try:
        db.add(new_ai_user_list)
        db.commit()
        db.refresh(new_ai_user_list)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model id: {ai_id}, user id sharer: {user_id_sharer}, user id beneficiary: {user_id_beneficiary} error sharing AI model!")
    return new_ai_user_list

def check_shared(user_id_beneficiary: int, ai_id: str, db: Session):
    entry = db.query(models.UserAIList).where(and_(models.UserAIList.fk_ai_id == ai_id, models.UserAIList.fk_user_id == user_id_beneficiary, models.UserAIList.beneficiary == True)).first()
    if not entry:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Ai model id: {ai_id} not shared with user id: {user_id_beneficiary}!")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Ai model id: {ai_id} already shared with user id: {user_id_beneficiary}!")


def user_shared_ai_list(user_id: int, db: Session):
    #check the user exists
    user.get_user_by_id(user_id, db)
    #get entries where user is the owner from UserAIList
    userai = db.query(models.UserAIList, models.AI, models.User).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.beneficiary == True).outerjoin(models.AI).outerjoin(models.User).all()
    if not userai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User id: {user_id}, does have shared AI models in the database!")
    return userai