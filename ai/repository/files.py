from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas, models
from typing import List
import uuid
import os
import shutil

def check_model_files(ai_id: str, db: Session):
    modelfiles = db.query(models.ModelFile).where(models.ModelFile.fk_ai_id == ai_id).all()
    modelfiles_name_path = db.query(models.ModelFile).where(models.ModelFile.fk_ai_id == ai_id).with_entities(models.ModelFile.name, models.ModelFile.path).all()
    if not modelfiles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no model files!")
    for modelfile in modelfiles:   
        if modelfile.path == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI model with id number {ai_id} does not have model files!")
        if os.path.isfile(modelfile.path) == False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI model with id number: {ai_id}, path: {modelfile.path}, does not exist in the filesystem !")
    return modelfiles_name_path

def delete_model_files(ai_id: str, db: Session):
    modelfiles = db.query(models.ModelFile).where(models.ModelFile.fk_ai_id == ai_id).all()
    if not modelfiles:
        return True
        """ raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no model files in database!") """
    try:
        modelfiles.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} error deleting from database!")
    return True

async def create_input_file(db: Session, input_file: UploadFile = File(...)):
    input_file_id = str(uuid.uuid4()).replace("-", "")
    file_name = input_file.filename
    file_path = "./inputfiles/" + input_file_id + "/" + file_name

    try:
        os.makedirs("./inputfiles/" + input_file_id, exist_ok=True)
        with open(f"{file_path}", "wb") as buffer:
                shutil.copyfileobj(input_file.file, buffer)  
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Input File with id number: {input_file_id} and name: {file_name} filesystem write error!")

    new_input_file = models.InputFile(input_file_id = input_file_id, name=file_name, path = file_path)

    try:
        db.add(new_input_file)
        db.commit()
        db.refresh(new_input_file)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Input File with id number {input_file_id} error creating InputFile table entry!")

    return new_input_file

def check_input_file(input_file_id: str, db: Session):
    input_file = db.query(models.InputFile).where(models.InputFile.input_file_id == input_file_id).first()
    inputfile_name_path = db.query(models.InputFile).where(models.InputFile.input_file_id == input_file_id).first()
    if not input_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Input file with id number {input_file_id} not found in database!")
    file_exists = os.path.isfile(input_file.path)
    if file_exists == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Input file with id number: {input_file_id}, path: {input_file.path}, does not exist in the filesystem !")
    return inputfile_name_path

async def create_pythonscript(ai_id: str, db: Session, python_file: UploadFile = File(...)):
    
    file_name = python_file.filename
    file_path = "./modelfiles/" + ai_id + "/" + file_name

    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
    #check if provided model_id is valid
    if not ai.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
    #check if model already has python script
    if ai.first().python_script_path != None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model id {ai_id} already has a python script!")
    #try to update ai data fields related to python script
    try:
        ai.update({"python_script_name": file_name, "python_script_path": file_path })
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model id {ai_id} database update error!")
    #try to write python script top filesystem
    try:
        os.makedirs("./modelfiles/" + ai_id, exist_ok=True)
        with open(f"{file_path}", "wb") as buffer:
            shutil.copyfileobj(python_file.file, buffer)  
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File named {file_name} filesystem write error!")

    return HTTPException(status_code=status.HTTP_200_OK, detail=f"The file named {file_name} was successfully submited to model id number {ai_id}.")

async def create_model_files(ai_id: str, db: Session, model_files: List[UploadFile] = File(...)):
    for model_file in model_files:
        file_name = model_file.filename
        file_path = "./modelfiles/" + ai_id + "/" + file_name

        ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
        #check if provided model_id is valid
        if not ai.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
        #create a new entry in the table model file
        try:
            new_modelfile = models.ModelFile(fk_ai_id=ai_id, name=file_name, path=file_path)
            db.add(new_modelfile)
            db.commit()
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model id {ai_id} database commit error!")
        #try to write python script top filesystem
        try:
            os.makedirs("./modelfiles/" + ai_id, exist_ok=True)
            with open(f"{file_path}", "wb") as buffer:
                shutil.copyfileobj(model_file.file, buffer)  
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File named {file_name} filesystem write error!")

    return HTTPException(status_code=status.HTTP_200_OK, detail=f"Files successfully submited to model id number {ai_id}.")