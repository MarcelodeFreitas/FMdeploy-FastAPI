from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import files, project
import shutil
import os

router = APIRouter(prefix="/files", tags=["Files"])


# upload input file
# authorization: any + login required
@router.post("/inputfile", status_code=status.HTTP_200_OK)
async def create_input_file(
    input_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return await files.create_input_file(db, input_file)


# upload python script
# authorization: admin or user that owns the project
@router.post("/pythonscript/{project_id}")
async def create_script_file(
    project_id: str,
    python_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return await files.create_python_script(
        current_user.email, current_user.role, project_id, db, python_file
    )


# upload modelfiles
# authorization: admin or user that owns the project
@router.post("/modelfiles/{project_id}")
async def create_model_file(
    project_id: str,
    model_files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return await files.create_model_files(
        current_user.email, current_user.role, project_id, db, model_files
    )


# get modelfiles name and path stored for a specific project
# authorization: any + login required
@router.post("/check_model_files/{project_id}", status_code=status.HTTP_200_OK)
def check_model_files_by_id(
    project_id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return files.check_model_files(project_id, db)


# get input file name and path stored by id
# authorization: any + login required
@router.post("/check_input_file/{input_file_id}", status_code=status.HTTP_200_OK)
def check_input_file_by_id(
    input_file_id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return files.check_input_file(input_file_id, db)


# check python file by id
# authorization: any + login required
@router.post("/check_python_file/{project_id}", status_code=status.HTTP_200_OK)
def check_python_file_by_id(
    project_id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return project.check_python_files(project_id, db)


# get input file by path
# authorization: admin or user
@router.get("/inputfile/{input_file_id}", status_code=status.HTTP_200_OK)
def get_input_file(
    input_file_id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return files.get_input_file_by_id(db, input_file_id)


# get output file by path
# authorization: admin or user
@router.get("/outputfile/{output_file_id}", status_code=status.HTTP_200_OK)
def get_output_file(
    output_file_id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return files.get_output_file_by_id(db, output_file_id)
