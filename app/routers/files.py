from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import files, project
import shutil
import os

router = APIRouter(
    prefix="/files",
    tags=['Files']
)

#upload input file
@router.post("/inputfile", status_code = status.HTTP_200_OK)
async def create_input_file(input_file: UploadFile = File(...), db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return await files.create_input_file(db, input_file)

#upload python script
@router.post("/pythonscript/{project_id}")
async def create_script_file(project_id: str, python_file: UploadFile = File(...), db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return await files.create_python_script(get_current_user, project_id, db, python_file)

#upload modelfiles 
@router.post("/modelfiles/{project_id}")
async def create_model_file(project_id: str, model_files: List[UploadFile] = File(...), db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return await files.create_model_files(get_current_user, project_id, db, model_files)

#get modelfiles name and path stored for a specific project
@router.post("/check_model_files/{project_id}", status_code = status.HTTP_200_OK)
def check_model_files_by_id(project_id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return files.check_model_files(project_id, db)

#get input file name and path stored by id
@router.post("/check_input_file/{input_file_id}", status_code = status.HTTP_200_OK)
def check_input_file_by_id(input_file_id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return files.check_input_file(input_file_id, db)

#get python file by id
@router.post("/check_python_file/{project_id}", status_code = status.HTTP_200_OK)
def check_python_file_by_id(project_id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.check_python_files(project_id, db)