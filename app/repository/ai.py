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
import logging

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
    #check permissions
    #check if owner or admin
    if not ((user.is_admin_bool(user_email, db)) or (userai.is_owner_bool(user_email, ai_id, db))):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with email: {user_email} does not have permissions to see AI model id: {ai_id}!")
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

""" def get_ai_by_title_exposed(user_email: str, title: str, db: Session):
    ai = db.query(models.AI).filter(models.AI.title.like(f"%{title}%")).all()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with title: {title} was not found!")
    return ai """

def create_ai_entry(ai_id: str, author: str, request: schemas.CreateAI, db: Session):
    new_ai = models.AI(ai_id = ai_id, author=author, title=request.title, description=request.description, input_type=request.input_type, output_type=request.output_type, is_private=request.is_private, created_in=datetime.now())
    try:
        db.add(new_ai)
        db.commit()
        db.refresh(new_ai)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} error creating AI table entry!")
    return new_ai

#useless since create_ai_entry has been changed to add author when ai is created
def create_ai_admin(user_email: str, request: schemas.CreateAI, db: Session):
    ai_id = str(uuid.uuid4().hex)
    #check admin
    user.user_is_admin(user_email, db)
    user.get_user_by_id(request.user_id, db)
    create_ai_entry(ai_id, request, db)
    userai.create_ai_user_list_entry(request.user_id, ai_id, db)
    return {"ai_id": ai_id}

def create_ai_current(request: schemas.CreateAI, user_email: str, db: Session):
    ai_id = str(uuid.uuid4().hex)
    user_object = user.get_user_by_email(user_email, db)
    create_ai_entry(ai_id, user_object.name, request, db)
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

async def run_ai_admin(current_user_email: str, user_id: int, ai_id: str, input_file_id: str, db: Session):
    #check permissions
    user.user_is_admin(current_user_email, db)
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

async def run_ai(current_user_email: str, ai_id: str, input_file_id: str, db: Session):
    #check if the user id provided exists
    user_id = user.get_user_by_email(current_user_email, db).user_id
    #check if the ai id provided exists
    model = get_ai_by_id(ai_id, db)
    print("hereeeee:" + model.input_type + model.output_type)
    #check if the ai model is public
    if not check_public_by_id(ai_id, db):
        #check if the user has access to this ai model
        #by checking the userailist table
        userai.check_access_ai_exception(user_id, ai_id, db)
    #check if input file exists
    input_file = files.check_input_file(input_file_id, db)
    input_file_name_no_extension = input_file.name.split(".")[0]
    #check if the ai table has python script paths
    #check that the python script files exist in the filesystem
    python_file = check_python_files(ai_id, db)
    print("WARNING: ", files.check_model_files_bool(ai_id, db))
    #check if this is an AI Model with or without model files
    if files.check_model_files_bool(ai_id, db):
        #check if the table modelfile has files associated with this ai model
        #check if those files exist in the file system
        model_files = files.check_model_files(ai_id, db)
        try:
            # run the ai model
            output_file_path = run_script(ai_id, python_file, model_files, input_file)
            #check if result file exists
            print("output file path hereeee:" + output_file_path + model.output_type)
            if not os.path.isfile(output_file_path + model.output_type):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no output file!")
            if (model.output_type == ".nii.gz"):
                return FileResponse(output_file_path + model.output_type, media_type="application/gzip", filename="result_" + input_file_name_no_extension + model.output_type)
            elif (model.output_type == ".csv"):
                return FileResponse(output_file_path + model.output_type, media_type="text/csv", filename="result_" + input_file_name_no_extension + model.output_type)
            elif (model.output_type == ".png"):
                return FileResponse(output_file_path + model.output_type, media_type="image/png", filename="result_" + input_file_name_no_extension + model.output_type)
            elif (model.output_type == ".wav"):
                return FileResponse(output_file_path + model.output_type, media_type="audio/wav", filename="result_" + input_file_name_no_extension + model.output_type)
        except:
            error = logging.exception("run_script error: ")
            print(error)
            """ raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Script error") """
            log_path = "./outputfiles/" + input_file.input_file_id + "/" + python_file.python_script_name[0:-3] + ".log"
            if not os.path.isfile(log_path):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no error log file!")
            return FileResponse(log_path, media_type="text/plain", filename=python_file.python_script_name[0:-3] + "_error_log")
        
    else:
        try:
            # run the ai model
            output_file_path = run_simple_script(ai_id, python_file, input_file)
            #check if result file exists
            print("output file path hereeee:" + output_file_path + model.output_type)
            if not os.path.isfile(output_file_path + model.output_type):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no output file!")
            if (model.output_type == ".nii.gz"):
                return FileResponse(output_file_path + model.output_type, media_type="application/gzip", filename="result_" + input_file_name_no_extension + model.output_type)
            elif (model.output_type == ".csv"):
                return FileResponse(output_file_path + model.output_type, media_type="text/csv", filename="result_" + input_file_name_no_extension + model.output_type)
            elif (model.output_type == ".png"):
                return FileResponse(output_file_path + model.output_type, media_type="image/png", filename="result_" + input_file_name_no_extension + model.output_type)
            elif (model.output_type == ".wav"):
                return FileResponse(output_file_path + model.output_type, media_type="audio/wav", filename="result_" + input_file_name_no_extension + model.output_type)
        except:
            error = logging.exception("run_script error: ")
            print(error)
            log_path = "./outputfiles/" + input_file.input_file_id + "/" + python_file.python_script_name[0:-3] + ".log"
            if not os.path.isfile(log_path):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no error log file!")
            return FileResponse(log_path, media_type="text/plain", filename=python_file.python_script_name[0:-3] + "_error_log")
            
            
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
    input_file_name_no_extension = input_file_name.split(".")[0]
    print("input_file_name_no_extension: ", input_file_name_no_extension)
    input_file_path = input_file.path
    input_directory_path = input_file_path.replace(input_file_name,"")
    # make output directory
    os.makedirs("./outputfiles/" + input_file.input_file_id, exist_ok=True)

    output_directory_path = "./outputfiles/" + input_file.input_file_id + "/"
    output_file_name = "result_" + input_file_name_no_extension
    print("output_file_name: ", output_file_name)
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
    try:
        logname = output_directory_path + python_script_name + ".log"
        print(logname)
        logging.basicConfig(filename=logname,
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
        print("LOAD MODELS:", script.load_models(model_files))
        print("RUN:", script.run(input_file_path, output_file_name, output_directory_path))
        
    except:
        error = logging.exception("run_script errors:")
        print(error)

    return output_directory_path + output_file_name

def run_simple_script( ai_id: str, python_file: dict, input_file: dict):
    python_script_name = python_file.python_script_name[0:-3]
    input_file_name = input_file.name
    input_file_name_no_extension = input_file_name.split(".")[0]
    print("input_file_name_no_extension: ", input_file_name_no_extension)
    input_file_path = input_file.path
    input_directory_path = input_file_path.replace(input_file_name,"")
    # make output directory
    os.makedirs("./outputfiles/" + input_file.input_file_id, exist_ok=True)
    output_directory_path = "./outputfiles/" + input_file.input_file_id + "/"
    output_file_name = "result_" + input_file_name_no_extension
    print("output_file_name: ", output_file_name)
    path = "./modelfiles/" + ai_id
    is_directory = os.path.isdir(path)
    if not is_directory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no file directory!")
    # add folder path to sys
    sys.path.append(path)
    # import the module
    script = importlib.import_module(python_script_name)
    # run "load_models" and "run"
    try:
        logname = output_directory_path + python_script_name + ".log"
        print(logname)
        logging.basicConfig(filename=logname,
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
        print("RUN:", script.run(input_file_path, output_file_name, output_directory_path))
        
    except:
        error = logging.exception("run_simple_script errors:")
        print(error)

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

def update_ai_by_id_exposed(user_email: str, ai_id: int, title: str, description: str, input_type: str, output_type: str, is_private: bool,  db: Session):
    #check permissions
    #check if owner or admin
    if not ((user.is_admin_bool(user_email, db)) or (userai.is_owner_bool(user_email, ai_id, db))):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with email: {user_email} does not have permissions to update AI model id: {ai_id}!")
    #check if ai exists
    ai = get_ai_query_by_id(ai_id, db)
    #check what data has been provided in the request
    #check if all request fields are empty or null
    if (title == "" or title == None) and (description == "" or description == None) and (input_type == "" or input_type == None) and (output_type == "" or output_type == None) and (is_private == "" or is_private == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Request AI model update fields are all empty!")
    # if a request field is empty or null keep the previous value
    #title
    if title == "" or title == None:
        title = ai.first().title
    #description
    if description == "" or description == None:
        description = ai.first().description
    #input_type
    if input_type == "" or input_type == None:
        input_type = ai.first().input_type
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
        ai.update({'input_type': input_type})
        ai.update({'output_type': output_type})
        ai.update({'is_private': is_private})
        ai.update({'last_updated': datetime.now()})
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"AI model with id: {ai_id} error updating database by User with email: {user_email}!")
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"AI model with id: {ai_id} was successfully updated by User with email: {user_email}.")