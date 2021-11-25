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

def get_owner(ai_id: str, db):
    user = db.query(models.User).where(and_(models.UserAIList.fk_ai_id == ai_id, models.UserAIList.owner == True)).outerjoin(models.UserAIList).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"error get_owner!")
    return user

def is_owner_bool(user_email: str, ai_id: str, db):
    user_id = user.get_user_by_email(user_email, db).user_id
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.fk_ai_id == ai_id).with_entities(models.UserAIList.owner).first()
    if not entry:
        return False
    return entry.owner

def delete(user_id: int, ai_id: str, db: Session):
    # entry = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.fk_ai_id == ai_id)
    # ajusted to delete the entry that identifies shared models, models that are deleted cant remain shared
    entry = db.query(models.UserAIList).where(models.UserAIList.fk_ai_id == ai_id)
    if not entry.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User id: {user_id}, ai model id: {ai_id} not found in database!")
    try:
        entry.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User id: {user_id}, ai model id: {ai_id} error deleting from database!")
    return True

def user_owned_ai_list(current_user_email: str, db: Session):
    #check the user exists
    user_id = user.get_user_by_email(current_user_email, db).user_id
    #get entries where user is the owner from UserAIList
    userai = db.query(models.UserAIList, models.AI, models.User).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.owner == True).outerjoin(models.AI).outerjoin(models.User).with_entities(models.AI.created_in, models.AI.author, models.AI.title, models.AI.ai_id, models.AI.description, models.AI.input_type, models.AI.output_type, models.AI.is_private, models.User.name).all()
    if not userai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User {current_user_email}, does not own any AI models!")
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
    new_ai_user_list = models.UserAIList(fk_user_id=user_id_beneficiary, fk_ai_id=ai_id,owner=False)
    try:
        db.add(new_ai_user_list)
        db.commit()
        db.refresh(new_ai_user_list)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model id: {ai_id}, user id sharer: {user_id_sharer}, user id beneficiary: {user_id_beneficiary} error sharing AI model!")
    return new_ai_user_list

def user_share_ai_exposed(current_user_email: str, beneficiary_email: str, ai_id: str, db: Session):
    #check if current_user_email is the same as beneficiary_email
    if (current_user_email == beneficiary_email):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"An Ai model can't be shared with the owner")
    #check the ai model exists
    ai_object = ai.get_ai_by_id(ai_id, db)
    if not (ai_object.is_private):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"This AI model is already public") 
    #check permissions
    #check if owner or admin
    if not ((user.is_admin_bool(current_user_email, db)) or (userai.is_owner_bool(current_user_email, ai_id, db))):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with email: {current_user_email} does not have permissions to share AI model id: {ai_id}!")
    #check the user exists
    user_id_sharer = user.get_user_by_email(current_user_email, db).user_id
    #check user beneficiary exists
    user_id_beneficiary = user.get_user_by_email(beneficiary_email, db).user_id
    #check if it is already shared with this user
    check_shared(user_id_beneficiary, ai_id, db)
    #create UserAi List table entry where owner=false and beneficiary=true
    new_ai_user_list = models.UserAIList(fk_user_id=user_id_beneficiary, fk_ai_id=ai_id,owner=False)
    try:
        db.add(new_ai_user_list)
        db.commit()
        db.refresh(new_ai_user_list)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model id: {ai_id}, sharer: {current_user_email}, user beneficiary: {beneficiary_email} error sharing AI model!")
    return f"AI model id:  {ai_id}, shared with {beneficiary_email}"

def user_cancel_share_ai(current_user_email: str, beneficiary_email: str, ai_id: str, db: Session):
    #check the ai model exists
    ai_object = ai.get_ai_by_id(ai_id, db)
    if not (ai_object.is_private):
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"This AI model is already public") 
    #check permissions
    #check if owner or admin
    if not ((user.is_admin_bool(current_user_email, db)) or (userai.is_owner_bool(current_user_email, ai_id, db))):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with email: {current_user_email} does not have permissions to share AI model id: {ai_id}!")
    #check the user exists
    user_id_sharer = user.get_user_by_email(current_user_email, db).user_id
    #check user beneficiary exists
    user_id_beneficiary = user.get_user_by_email(beneficiary_email, db).user_id
    #check if it is shared with this user
    userai_entry = check_shared_entry(user_id_beneficiary, ai_id, db)
    #deleting entry from userai list
    try:
        userai_entry.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model id: {ai_id}, sharer: {current_user_email}, user beneficiary: {beneficiary_email} error canceling share AI model!")
    return f"AI model id:  {ai_id}, not shared with {beneficiary_email}"

def check_shared(user_id_beneficiary: int, ai_id: str, db: Session):
    entry = db.query(models.UserAIList).where(and_(models.UserAIList.fk_ai_id == ai_id, models.UserAIList.fk_user_id == user_id_beneficiary, models.UserAIList.owner == False)).first()
    if not entry:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Ai model id: {ai_id} not shared with user!")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Ai model id: {ai_id} already shared with user!")

def check_shared_entry(user_id_beneficiary: int, ai_id: str, db: Session):
    print(user_id_beneficiary)
    entry = db.query(models.UserAIList).where(and_(models.UserAIList.fk_ai_id == ai_id, models.UserAIList.fk_user_id == user_id_beneficiary, models.UserAIList.owner == False))
    if not entry.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Ai model id: {ai_id} not shared with user {user_id_beneficiary}!")
    else:
        return entry

def user_shared_ai_list(user_id: int, db: Session):
    #check the user exists
    user.get_user_by_id(user_id, db)
    #get entries where user is the owner from UserAIList
    userai = db.query(models.UserAIList, models.AI, models.User).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.owner == False).outerjoin(models.AI).outerjoin(models.User).all()
    if not userai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User id: {user_id}, does have shared AI models in the database!")
    return userai

def user_shared_ai_list_exposed(current_user_email: str, db: Session):
    #check the user exists
    user_id = user.get_user_by_email(current_user_email, db).user_id
    #get entries where user is the beneficiary from UserAIList
    userai = db.query(models.UserAIList, models.AI, models.User).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.owner == False).outerjoin(models.AI).outerjoin(models.User).with_entities(models.AI.created_in, models.AI.author, models.AI.title, models.AI.ai_id, models.AI.description, models.AI.input_type, models.AI.output_type, models.AI.is_private).all()
    if not userai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User {current_user_email}, does not have any shared AI models!")
    return userai

def create_ai_user_list_entry(user_id: str, ai_id: int, db: Session):
    new_ai_user_list = models.UserAIList(fk_user_id=user_id, fk_ai_id=ai_id,owner=True)
    try:
        db.add(new_ai_user_list)
        db.commit()
        db.refresh(new_ai_user_list)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} error creating AIUserList table entry!")
    return new_ai_user_list

#get the list of user that a certain Ai model has been shared with
def check_beneficiaries(ai_id: str, current_user_email: str, db: Session):
    #check credentials
    #check if owner or admin
    if not ((user.is_admin_bool(current_user_email, db)) or (is_owner_bool(current_user_email, ai_id, db))):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with email: {current_user_email} does not have permissions to check beneficiaries of AI model id: {ai_id}!")
    userai = db.query(models.UserAIList, models.User).where(models.UserAIList.fk_ai_id == ai_id).where(models.UserAIList.owner == False).outerjoin(models.User).with_entities(models.User.name, models.User.email).all()
    if not userai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"The AI Model id: {ai_id} has not been shared!")
    return userai