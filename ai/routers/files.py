from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import ai, files
import shutil
import os

router = APIRouter(
    prefix="/files",
    tags=['Files']
)

#upload input file
@router.post("/inputfile", status_code = status.HTTP_200_OK)
async def create_input_file(file: UploadFile = File(...), db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return files.create_input_file(db, file)

#upload python script
@router.post("/pythonscript/{ai_id}")
async def create_script_file(ai_id: str, python_file: UploadFile = File(...), db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return files.create_pythonscript(ai_id, db, python_file)

#upload model files 
@router.post("/modelfiles/{ai_id}")
async def create_model_file(ai_id: str, model_files: List[UploadFile] = File(...), db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
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

#get model files name and path stored for a specific ai model
@router.post("/check_model_files/{ai_id}", status_code = status.HTTP_200_OK)
def check_model_files_by_id(ai_id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return files.check_model_files(ai_id, db)

#get input file name and path stored by id
@router.post("/check_input_file/{input_file_id}", status_code = status.HTTP_200_OK)
def check_input_file_by_id(input_file_id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return files.check_input_file(input_file_id, db)

#get python file by id
@router.post("/check_python_file/{ai_id}", status_code = status.HTTP_200_OK)
def check_python_file_by_id(ai_id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.check_python_files(ai_id, db)