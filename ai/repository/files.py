from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas, models
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

def create_input_file(db: Session, file: UploadFile = File(...)):
    input_file_id = str(uuid.uuid4()).replace("-", "")
    file_name = file.filename
    file_path = "./inputfiles/" + input_file_id + "/" + file_name

    try:
        os.makedirs("./inputfiles/" + input_file_id, exist_ok=True)
        with open(f"{file_path}", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)  
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
    inputfile_name_path = db.query(models.InputFile).where(models.InputFile.input_file_id == input_file_id).with_entities(models.InputFile.name, models.InputFile.path).first()
    if not input_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Input file with id number {input_file_id} not found in database!")
    file_exists = os.path.isfile(input_file.path)
    if file_exists == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Input file with id number: {input_file_id}, path: {input_file.path}, does not exist in the filesystem !")
    return inputfile_name_path