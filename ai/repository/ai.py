from fastapi import HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .. import schemas, models
from . import user, userai, files
import uuid
from typing import List
import importlib
import sys
import os
import shutil
from datetime import datetime

def get_all(db: Session):
    ai_list = db.query(models.AI).all()
    if not ai_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"No AI models found in the database!")
    return ai_list

def get_all_exposed(user_email: str, db: Session):
    #check if admin
    user.user_is_admin(user_email, db)
    #listall ai models
    ai_list = db.query(models.AI).all()
    if not ai_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"No AI models found in the database!")
    return ai_list

def get_all_public(db: Session):
    ai_list =  db.query(models.AI).where(models.AI.is_private.is_(False)).all()
    if not ai_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"No public AI models found in the database!")
    return ai_list

def get_public_by_id_exposed(ai_id: str, db: Session):
    ai =  db.query(models.AI).where(models.AI.is_private.is_(False)).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found in Public AIs!")
    return ai

def get_public_by_title_exposed(title: str, db: Session):
    ai = db.query(models.AI).where(models.AI.is_private.is_(False)).filter(models.AI.title.like(f"%{title}%")).all()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with title: {title} was not found!")
    return ai

def get_ai_by_id_exposed(user_email: str, ai_id: str, db: Session):
    #check if user is admin
    user.user_is_admin(user_email, db)
    #get ai by id
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found!")
    return ai

def get_ai_by_title(title: str, db: Session):
    ai = db.query(models.AI).filter(models.AI.title.like(f"%{title}%")).all()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with title: {title} was not found!")
    return ai

def create_ai_entry(ai_id: str, request: schemas.CreateAI, db: Session):
    new_ai = models.AI(ai_id = ai_id, title=request.title, description=request.description, output_type=request.output_type,is_private=request.is_private, created_in=datetime.now())
    try:
        db.add(new_ai)
        db.commit()
        db.refresh(new_ai)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} error creating AI table entry!")
    return new_ai

def create_ai_admin(user_email: str, request: schemas.CreateAI, db: Session):
    ai_id = str(uuid.uuid4()).replace("-", "")
    #check admin
    user.user_is_admin(user_email, db)
    user.get_user_by_id(request.user_id, db)
    create_ai_entry(ai_id, request, db)
    userai.create_ai_user_list_entry(request.user_id, ai_id, db)
    return {"ai_id": ai_id}

def create_ai_current(request: schemas.CreateAI, user_email: str, db: Session):
    ai_id = str(uuid.uuid4()).replace("-", "")
    user_object = user.get_user_by_email(user_email, db)
    create_ai_entry(ai_id, request, db)
    userai.create_ai_user_list_entry(user_object.user_id, ai_id, db)
    return {"ai_id": ai_id}

def get_ai_by_id(ai_id: str, db: Session):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found!")
    return ai

def get_ai_query_by_id(ai_id: str, db: Session):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
    if not ai.first():
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
    #check if the ai table has python script paths
    #check that the python script files exist in the filesystem
    python_file = check_python_files(ai_id, db)
    #check if the table modelfile has files associated with this ai model
    #check if those files exist in the file system
    model_files = files.check_model_files(ai_id, db)
    # run the ai model
    output_file_path = run_script(ai_id, python_file, model_files, input_file)
    #check if result file exists
    if not os.path.isfile(output_file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"There is no output file at: {output_file_path}!")
    
    return FileResponse(output_file_path, media_type="application/gzip", filename="result_" + input_file.name)

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
    script.run(input_file_path, output_file_name, output_directory_path)

    return output_directory_path + output_file_name

def delete(user_email: str, ai_id: str, db: Session):
    #check if the ai exists
    get_ai_by_id(ai_id, db)
    #get current user id
    user_id = user.get_user_by_email(user_email, db).user_id
    #check permissions
    #only the owner can delete ai model
    userai.check_owner(user_id, ai_id, db)
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
    #delete ai folder from filesystem
    path = "./modelfiles/" + ai_id
    if not os.path.isdir(path):
        pass
        """ raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no file directory!") """
    try:
        shutil.rmtree(path)
    except:
        pass
        """ raise HTTPException(status_code=status.HTTP_200_OK,
         detail=f"AI model with id number {ai_id} has no directory in the filesystem!") """
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"The AI model id {ai_id} was successfully deleted.")

def delete_admin(user_email: str, ai_id: str, db: Session):
    #check if the ai exists
    ai_object = get_ai_by_id(ai_id, db)
    #check permissions
    user.user_is_admin(user_email, db)
    #get owner id for ai model
    owner_id = userai.get_owner(ai_id, db).user_id
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
    userai.delete(owner_id, ai_id, db)
    #deleter from ModelFile table
    files.delete_model_files(ai_id, db)
    #delete ai folder from filesystem
    path = "./modelfiles/" + ai_id
    if not os.path.isdir(path):
        pass
        """ raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no file directory!") """
    try:
        shutil.rmtree(path)
    except:
        pass
        """ raise HTTPException(status_code=status.HTTP_200_OK,
         detail=f"AI model with id number {ai_id} has no directory in the filesystem!") """
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"The AI model id {ai_id} was successfully deleted.")

def update_ai_by_id_exposed(user_email: str, ai_id: int, title: str, description: str, output_type: str, is_private: bool,  db: Session):
    #check permissions
    #check if owner or admin
    if not ((user.is_admin_bool(user_email, db)) or (userai.is_owner_bool(user_email, ai_id, db))):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with email: {user_email} does not have permissions to update AI model id: {ai_id}!")
    #check if ai exists
    ai = get_ai_query_by_id(ai_id, db)
    #check what data has been provided in the request
    #check if all request fields are empty or null
    if (title == "" or title == None) and (description == "" or description == None) and (output_type == "" or output_type == None) and (is_private == "" or is_private == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Request AI model update fields are all empty!")
    # if a request field is empty or null keep the previous value
    #title
    if title == "" or title == None:
        title = ai.first().title
    #description
    if description == "" or description == None:
        description = ai.first().description
    #output_type
    if output_type == "" or output_type == None:
        output_type = ai.first().output_type
    #is_private
    if is_private == "" or is_private == None:
        is_private = ai.first().is_private
    #update ai in database
    try:
        ai.update({'title': title})
        ai.update({'description': description})
        ai.update({'output_type': output_type})
        ai.update({'is_private': is_private})
        ai.update({'last_updated': datetime.now()})
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"AI model with id: {ai_id} error updating database by User with email: {user_email}!")
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"AI model with id: {ai_id} was successfully updated by User with email: {user_email}.")