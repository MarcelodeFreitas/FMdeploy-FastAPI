from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas, models
from . import user, userai, files
import uuid
from typing import List
import importlib
import sys
import os
import shutil

# print(str(uuid.uuid4()).replace("-", ""))

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
    new_ai_user_list = models.UserAIList(fk_user_id=user_id, fk_ai_id=ai_id,owner=True, beneficiary=False)
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

async def run_ai(user_id: int, ai_id: str, input_file_id: str, db: Session):
    #check if the user id provided exists
    user.get_user_by_id(user_id, db)
    #check if the ai id provided exists
    get_ai_by_id(ai_id, db)
    #check if the ai model is public
    if not check_public_by_id(ai_id, db):
        #check if the user has access to this ai model
        #by checking the userailist table
        userai.check_access_ai_exception(user_id, ai_id, db)
    #check if input file exists
    input_file = files.check_input_file(input_file_id, db)
    print(input_file)
    #check if the ai table has python script paths
    #check that the python script files exist in the filesystem
    python_file = check_python_files(ai_id, db)
    #check if the table modelfile has files associated with this ai model
    #check if those files exist in the file system
    model_files = files.check_model_files(ai_id, db)
    # run the ai model
    run_script(ai_id, python_file, model_files, input_file)
    return "hey"

def check_python_files(ai_id: str, db: Session):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id).first()
    name_path = db.query(models.AI).filter(models.AI.ai_id == ai_id).with_entities(models.AI.python_script_name, models.AI.python_script_path).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found!")
    if ai.python_script_path == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} does not have a python script!")
    file_exists = os.path.isfile(ai.python_script_path)
    return name_path

def run_script( ai_id: str, python_file: dict, model_files: dict, input_file: dict):
    python_script_name = python_file.python_script_name[0:-3]
    input_file_name = input_file.name
    input_file_path = input_file.path
    # make output directory
    os.makedirs("./outputfiles/" + input_file.input_file_id, exist_ok=True)

    output_directory_path = "./outputfiles/" + input_file.input_file_id + "/"
    output_file_name = "result_" + input_file_name
    path = "./modelfiles/" + ai_id

    #python_script_name = db.query(models.AI).where(models.AI.ai_id == ai_id).first().python_script_name[0:-3]
    is_directory = os.path.isdir(path)
    if not is_directory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no file directory!")
    # add folder path to sys
    sys.path.append(path)
    # import the module
    script = importlib.import_module(python_script_name)
    # run "load_models" and "run"
    script.load_models(model_files)

    return script.run(input_file_path, output_file_name, output_directory_path)

def delete(user_id: int, ai_id: str, db: Session):
    #check if the user exists
    user.get_user_by_id(user_id, db)
    #check if the ai exists
    get_ai_by_id(ai_id, db)
    #check if the user is the owner
    is_owner = userai.check_owner(user_id, ai_id, db)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with id: {user_id} is not the owner of the AI model id: {ai_id}!")
    #delete ai folder from filesystem
    path = "./modelfiles/" + ai_id
    if not os.path.isdir(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no file directory!")
    try:
        shutil.rmtree(path)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no directory in the filesystem!")
    #delete ai from database
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
    if not ai.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
    try:
        ai.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} error deleting from database!")
    #delete from UserAI List
    userai.delete(user_id, ai_id, db)
    #deleter from ModelFile table
    files.delete_model_files(ai_id, db)
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"The AI model id {ai_id} was successfully deleted.")