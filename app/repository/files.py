from fastapi import HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import models
from typing import List
import uuid
import os
import shutil
from . import user, userproject
import sys
import importlib
from .user import UserRole


# handle upload for input file
async def create_input_file(db: Session, input_file: UploadFile = File(...)):
    # create unique id for input file
    input_file_id = str(uuid.uuid4()).replace("-", "")

    file_name = input_file.filename
    file_path = "./inputfiles/" + input_file_id + "/" + file_name

    # create directory for input file and save file in it
    try:
        os.makedirs("./inputfiles/" + input_file_id, exist_ok=True)
        with open(f"{file_path}", "wb") as buffer:
            shutil.copyfileobj(input_file.file, buffer)
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Input File with id number: {input_file_id} and name: {file_name} filesystem write error: {e}",
        )

    new_input_file = models.InputFile(
        input_file_id=input_file_id, name=file_name, path=file_path
    )
    # add input file to database
    try:
        db.add(new_input_file)
        db.commit()
        db.refresh(new_input_file)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Input File with id number {input_file_id} error creating InputFile table entry: {e}",
        )

    return new_input_file


def check_model_files(project_id: str, db: Session):
    modelfiles = (
        db.query(models.ModelFile)
        .where(models.ModelFile.fk_project_id == project_id)
        .all()
    )
    modelfiles_name_path = (
        db.query(models.ModelFile)
        .where(models.ModelFile.fk_project_id == project_id)
        .with_entities(models.ModelFile.name, models.ModelFile.path)
        .all()
    )
    if not modelfiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} has no model files!",
        )
    for modelfile in modelfiles:
        if modelfile.path == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id number {project_id} does not have model files!",
            )
        if os.path.isfile(modelfile.path) == False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id number: {project_id}, path: {modelfile.path}, does not exist in the filesystem !",
            )
    return modelfiles_name_path


def check_model_files_bool(project_id: str, db: Session):
    modelfiles = (
        db.query(models.ModelFile)
        .where(models.ModelFile.fk_project_id == project_id)
        .all()
    )
    if modelfiles:
        return True
    else:
        return False


def delete_model_files(project_id: str, db: Session):
    modelfiles = (
        db.query(models.ModelFile)
        .where(models.ModelFile.fk_project_id == project_id)
        .all()
    )
    if not modelfiles:
        return True
        """ raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Project with id number {project_id} has no model files in database!") """
    try:
        for modelfile in modelfiles:
            """modelfile.delete(synchronize_session=False)"""
            db.delete(modelfile)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project files with id number {project_id} error deleting from database!",
        )
    return True


def check_input_file(input_file_id: str, db: Session):
    input_file = (
        db.query(models.InputFile)
        .where(models.InputFile.input_file_id == input_file_id)
        .first()
    )
    inputfile_name_path = (
        db.query(models.InputFile)
        .where(models.InputFile.input_file_id == input_file_id)
        .first()
    )
    if not input_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Input file with id number {input_file_id} not found in database!",
        )
    file_exists = os.path.isfile(input_file.path)
    if file_exists == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Input file with id number: {input_file_id}, path: {input_file.path}, does not exist in the filesystem !",
        )
    return inputfile_name_path


# handle pythonscript upload to filesystem and database associated with a specific project
async def create_python_script(
    current_user_email: str,
    user_role: UserRole,
    project_id: str,
    db: Session,
    python_file: UploadFile = File(...),
):
    # check if "user" is owner
    if user_role == UserRole.user:
        is_owner = userproject.is_owner_bool(current_user_email, project_id, db)
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {current_user_email} is not authorized to upload python scripts!",
            )

    file_name = python_file.filename
    file_path = "./modelfiles/" + project_id + "/" + file_name

    project = db.query(models.Project).filter(models.Project.project_id == project_id)
    # check if provided model_id is valid
    if not project.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found!",
        )
    # check if project already has python script
    if project.first().python_script_path != None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project id {project_id} already has a python script!",
        )
    # try to update project data fields related to python script
    try:
        project.update(
            {"python_script_name": file_name, "python_script_path": file_path}
        )
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project id {project_id} database update error!",
        )
    # try to write python script to filesystem
    try:
        os.makedirs("./modelfiles/" + project_id, exist_ok=True)
        with open(f"{file_path}", "wb") as buffer:
            shutil.copyfileobj(python_file.file, buffer)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File named {file_name} filesystem write error!",
        )
    # check if the python script saved is valid
    validate_python_script(project_id, file_name)

    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"The file named {file_name} was successfully submited to model id number {project_id}.",
    )


def validate_python_script(project_id: str, script_name: str):
    path = "./modelfiles/" + project_id
    print("file_name: ", script_name)
    script_name_without_extension = script_name[0:-3]
    # add folder path to sys
    sys.path.append(path)
    # import the module
    script = importlib.import_module(script_name_without_extension)
    # check if a name is in a module
    print("test1:", "load_models" in dir(script))
    print("test2:", "run" in dir(script))
    """ if ('load_models' in dir(script)) and ('run' in dir(script)):
        return True
    elif ('load_models' not in dir(script)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File named {script_name} is missing the function 'load_models' but may still run!") """
    if "run" not in dir(script):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File named {script_name} is missing the function 'run'!",
        )
    """ else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File named {script_name} is missing the functions 'load_models', 'run' or both!") """


async def create_model_files(
    current_user_email: str,
    user_role: UserRole,
    project_id: str,
    db: Session,
    model_files: List[UploadFile] = File(...),
):
    # check if "user" is owner
    if user_role == UserRole.user:
        is_owner = userproject.is_owner_bool(current_user_email, project_id, db)
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {current_user_email} is not authorized to upload model files!",
            )

    for model_file in model_files:
        file_name = model_file.filename
        file_path = "./modelfiles/" + project_id + "/" + file_name

        project = db.query(models.Project).filter(
            models.Project.project_id == project_id
        )
        # check if provided model_id is valid
        if not project.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found!",
            )
        # create a new entry in the table modelfile
        try:
            new_modelfile = models.ModelFile(
                fk_project_id=project_id, name=file_name, path=file_path
            )
            db.add(new_modelfile)
            db.commit()
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project id {project_id} database commit error!",
            )
        # try to write python script top filesystem
        try:
            os.makedirs("./modelfiles/" + project_id, exist_ok=True)
            with open(f"{file_path}", "wb") as buffer:
                shutil.copyfileobj(model_file.file, buffer)
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File named {file_name} filesystem write error!",
            )

    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"Files successfully submited to model id number {project_id}.",
    )


# create output file entry in database and save in local storage
def create_output_file_entry(
    db: Session, output_file_id: str, output_file_name: str, output_file_path: str
):
    output_file_id = models.OutputFile(
        output_file_id=output_file_id, name=output_file_name, path=output_file_path
    )
    try:
        db.add(output_file_id)
        db.commit()
        db.refresh(output_file_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Output File with id number {output_file_id} error creating OutputFile table entry!",
        )


# get input file by id
def get_input_file_by_id(db: Session, input_file_id: str):
    print("input_file_id: ", input_file_id)
    input_file = (
        db.query(models.InputFile, models.RunHistory, models.Project)
        .select_from(models.InputFile)  # Specify the table to join from
        .where(models.InputFile.input_file_id == input_file_id)
        .outerjoin(models.RunHistory)
        .outerjoin(models.Project)
        .with_entities(
            models.InputFile.input_file_id.label("id"),
            models.InputFile.name,
            models.InputFile.path,
            models.Project.input_type.label("type"),
        )
        .first()
    )
    print("input_file: ", input_file)

    if not input_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Input File with id number {input_file_id} not found!",
        )

    if not os.path.isfile(input_file.path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Input File with id {input_file_id} not found!",
        )

    media_type_dict = {
        ".nii.gz": ("application/gzip", ".nii.gz"),
        ".csv": ("text/csv", ".csv"),
        ".png": ("image/png", ".png"),
        ".wav": ("audio/wav", ".wav"),
    }

    if input_file.type in media_type_dict:
        media_type, file_ext = media_type_dict[input_file.type]
        return FileResponse(
            input_file.path,
            media_type=media_type,
            filename=input_file.name,
        )


# get outputfile by id
def get_output_file_by_id(db: Session, output_file_id: str):
    output_file = (
        db.query(models.OutputFile, models.RunHistory, models.Project)
        .select_from(models.OutputFile)  # Specify the table to join from
        .where(models.OutputFile.output_file_id == output_file_id)
        .outerjoin(models.RunHistory)
        .outerjoin(models.Project)
        .with_entities(
            models.OutputFile.output_file_id.label("id"),
            models.OutputFile.name,
            models.OutputFile.path,
            models.Project.output_type.label("type"),
        )
        .first()
    )
    print("output_file: ", output_file)

    if not output_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Output File with id number {output_file_id} not found!",
        )

    if not os.path.isfile(output_file.path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Output File with id {output_file_id} not found!",
        )

    media_type_dict = {
        ".nii.gz": ("application/gzip", ".nii.gz"),
        ".csv": ("text/csv", ".csv"),
        ".png": ("image/png", ".png"),
        ".wav": ("audio/wav", ".wav"),
    }

    if output_file.type in media_type_dict:
        media_type, file_ext = media_type_dict[output_file.type]
        return FileResponse(
            output_file.path,
            media_type=media_type,
            filename=output_file.name,
        )
