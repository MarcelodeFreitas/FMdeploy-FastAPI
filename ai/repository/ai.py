from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from . import user, userai, files
import uuid
import importlib
import sys
import os

print(str(uuid.uuid4()).replace("-", ""))

def get_all(db: Session):
    ai_list = db.query(models.AI).all()
    return ai_list

def create_ai_entry(ai_id: str, request: schemas.CreateAI, db: Session):
    new_ai = models.AI(ai_id = ai_id, title=request.title, description=request.description, output_type=request.output_type,is_private=request.is_private, created_in=request.created_in)
    try:
        db.add(new_ai)
        db.commit()
        db.refresh(new_ai)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} error creating AI table entry!")
    return new_ai

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

def create_ai(request: schemas.CreateAI, db: Session):
    ai_id = str(uuid.uuid4()).replace("-", "")
    user.get_user_by_id(request.user_id, db)
    create_ai_entry(ai_id, request, db)
    create_ai_user_list_entry(request.user_id, ai_id, db)
    return {"ai_id": ai_id}

def get_ai_by_id(ai_id: str, db: Session):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found!")
    return ai

def check_public_by_id(ai_id: str, db: Session):
    ai =  db.query(models.AI).where(models.AI.is_private.is_(False)).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        return False
    return True

async def run_ai(user_id: int, ai_id: str, db: Session):
    #check if the user id provided exists
    user.get_user_by_id(user_id, db)
    #check if the ai model is public
    if not check_public_by_id(ai_id, db):
        #check if the user has access to this ai model
        #by checking the userailist table
        userai.check_access_ai_exception(user_id, ai_id, db)
    #check if the ai table has python script paths
    #check that the python script files exist in the filesystem
    check_python_files(ai_id, db)
    #check if the table modelfile has files associated with this ai model
    #check if those files exist in the file system
    files.check_model_files(ai_id, db)
    # run the ai model
    # path = models.UserAIList
    # sys.path.append('./modelfiles/app')
    # script =  importlib.import_module("script")
    return "hey"

def check_python_files(ai_id: str, db):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found!")
    if ai.python_script_path == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} does not have a python script!")
    file_exists = os.path.isfile(ai.python_script_path)
    return file_exists

def run():
    pass


