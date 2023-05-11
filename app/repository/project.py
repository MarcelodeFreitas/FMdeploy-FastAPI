from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, models
from . import user, files, userproject, runhistory
from .user import UserRole
import uuid
from typing import Optional, List
import importlib
import sys
import os
import shutil
from datetime import datetime
import logging


# get all projects from database
def get_all(db: Session):
    # list all projects
    project_list = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.UserProject.owner == True)
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.project_id,
            models.User.name,
            models.Project.title,
            models.Project.description,
            models.Project.input_type,
            models.Project.output_type,
            models.Project.is_private,
            models.Project.created_in,
            models.Project.last_updated,
        )
        .all()
    )
    if not project_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No projects found in the database!",
        )
    return project_list


# get all the public projects from the database
def get_all_public(db: Session):
    project_list = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.Project.is_private.is_(False))
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.project_id,
            models.User.name,
            models.Project.title,
            models.Project.description,
            models.Project.input_type,
            models.Project.output_type,
            models.Project.is_private,
            models.Project.created_in,
            models.Project.last_updated,
        )
        .all()
    )
    if not project_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No public projects found in the database!",
        )
    return project_list


# get public project by id
def get_public_by_id(project_id: str, db: Session):
    project = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.Project.project_id == project_id)
        .where(models.Project.is_private.is_(False))
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.project_id,
            models.User.name,
            models.Project.title,
            models.Project.description,
            models.Project.input_type,
            models.Project.output_type,
            models.Project.is_private,
            models.Project.created_in,
            models.Project.last_updated,
        )
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} was not found in Public Projects!",
        )
    return project


# get public project by title
def get_public_by_title(title: str, db: Session):
    project = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.Project.is_private.is_(False))
        .filter(models.Project.title.like(f"%{title}%"))
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.project_id,
            models.User.name,
            models.Project.title,
            models.Project.description,
            models.Project.input_type,
            models.Project.output_type,
            models.Project.is_private,
            models.Project.created_in,
            models.Project.last_updated,
        )
        .all()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with title: {title} was not found in Public Projects!",
        )
    return project


# get project by id for internal user
def get_by_id(project_id: str, db: Session):
    # get project and author by project id
    project = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.UserProject.owner == True)
        .where(models.Project.project_id == project_id)
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.project_id,
            models.User.name,
            models.Project.title,
            models.Project.description,
            models.Project.input_type,
            models.Project.output_type,
            models.Project.is_private,
            models.Project.created_in,
            models.Project.last_updated,
        )
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} was not found!",
        )
    return project


# get project by id for admin, user or guest with access to the project
def get_by_id_exposed(
    user_email: str, user_role: UserRole, project_id: str, db: Session
):
    # check permissions
    # check if the project is public
    if not check_public_by_id_bool(project_id, db):
        # check if owner or admin or beneficiary (guest with access to the project)
        user_id = user.get_by_email(user_email, db).user_id
        if not (
            (user_role == "admin")
            or (userproject.is_owner_bool(user_email, project_id, db))
            or (userproject.check_access(user_id, project_id, db))
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with email: {user_email} does not have permissions to see Project id: {project_id}!",
            )
    # get project and author by project id
    project = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.UserProject.owner == True)
        .where(models.Project.project_id == project_id)
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.project_id,
            models.User.name,
            models.Project.title,
            models.Project.description,
            models.Project.input_type,
            models.Project.output_type,
            models.Project.is_private,
            models.Project.created_in,
            models.Project.last_updated,
        )
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} was not found!",
        )
    return project


def get_by_title_exposed(title: str, db: Session):
    project_list = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.UserProject.owner == True)
        .filter(models.Project.title.like(f"%{title}%"))
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.project_id,
            models.User.name,
            models.Project.title,
            models.Project.description,
            models.Project.input_type,
            models.Project.output_type,
            models.Project.is_private,
            models.Project.created_in,
            models.Project.last_updated,
        )
        .all()
    )
    if not project_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with title '{title}' was not found!",
        )
    return project_list


def create_project_entry(project_id: str, request: schemas.CreateProject, db: Session):
    new_project = models.Project(
        project_id=project_id,
        title=request.title,
        description=request.description,
        input_type=request.input_type,
        output_type=request.output_type,
        is_private=request.is_private,
        created_in=datetime.now(),
    )
    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} error creating Project table entry!",
        )
    return new_project


def create(request: schemas.CreateProject, user_email: str, db: Session):
    project_id = str(uuid.uuid4().hex)
    user_object = user.get_by_email(user_email, db)
    create_project_entry(project_id, request, db)
    userproject.create_project_user_entry(user_object.user_id, project_id, db)
    return {"project_id": project_id}


def get_by_id(project_id: str, db: Session):
    project = (
        db.query(models.Project).filter(models.Project.project_id == project_id).first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} not found!",
        )
    return project


def get_query_by_id(project_id: str, db: Session):
    project = db.query(models.Project).filter(models.Project.project_id == project_id)
    if not project.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} not found!",
        )
    return project


def check_public_by_id_bool(project_id: str, db: Session):
    project = (
        db.query(models.Project)
        .where(models.Project.is_private.is_(False))
        .filter(models.Project.project_id == project_id)
        .first()
    )
    if not project:
        return False
    return True


async def run(
    user_email: str,
    user_role: UserRole,
    project_id: str,
    input_file_id: str,
    db: Session,
):
    # check if the user id provided exists
    user_id = user.get_by_email(user_email, db).user_id
    # check if the project id provided exists
    project = get_by_id(project_id, db)
    # check permissions
    # check if the project is public
    if not check_public_by_id_bool(project_id, db):
        # check if owner or admin or beneficiary
        user_id = user.get_by_email(user_email, db).user_id
        if not (
            (user_role == "admin")
            or (userproject.is_owner_bool(user_email, project_id, db))
            or (userproject.check_access(user_id, project_id, db))
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with email: {user_email} does not have permissions to see Project id: {project_id}!",
            )
    print("input type:", project.input_type, "output type:", project.output_type)
    # check if input file exists
    input_file = files.check_input_file(input_file_id, db)
    input_file_name_no_extension = input_file.name.split(".")[0]
    # check if the project table has python script paths
    # check that the python script files exist in the filesystem
    python_file = check_python_files(project_id, db)
    print("CHECK MODEL FILES EXIST: ", files.check_model_files_bool(project_id, db))
    # check if this is a Project with or without modelfiles
    if files.check_model_files_bool(project_id, db):
        # check if the table modelfile has files associated with this project
        # check if those files exist in the file system
        model_files = files.check_model_files(project_id, db)
        # register in the run history table
        run_history_id = runhistory.create_entry(
            db, user_id, project_id, input_file_id, None, False, None
        )
        try:
            # run the project
            output_file_path = run_script(
                db,
                project_id,
                python_file,
                model_files,
                input_file,
                project.output_type,
                run_history_id,
            )
            # check if result file exists
            print("OUTPUT FILE PATH:" + output_file_path + project.output_type)
            if not os.path.isfile(output_file_path + project.output_type):
                print("ERROR3")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="There is no output file!",
                )
            """ if project.output_type == ".nii.gz":
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type="application/gzip",
                    filename="result_"
                    + input_file_name_no_extension
                    + project.output_type,
                )
            elif project.output_type == ".csv":
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type="text/csv",
                    filename="result_"
                    + input_file_name_no_extension
                    + project.output_type,
                )
            elif project.output_type == ".png":
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type="image/png",
                    filename="result_"
                    + input_file_name_no_extension
                    + project.output_type,
                )
            elif project.output_type == ".wav":
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type="audio/wav",
                    filename="result_"
                    + input_file_name_no_extension
                    + project.output_type,
                ) """
            media_type_dict = {
                ".nii.gz": ("application/gzip", ".nii.gz"),
                ".csv": ("text/csv", ".csv"),
                ".png": ("image/png", ".png"),
                ".wav": ("audio/wav", ".wav"),
            }

            if project.output_type in media_type_dict:
                media_type, file_ext = media_type_dict[project.output_type]
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type=media_type,
                    filename="result_" + input_file_name_no_extension + file_ext,
                )
        except Exception as e:
            """raise Exception(f"Error running porject: Error message: {str(e)}")"""
            log_path = (
                "./outputfiles/"
                + input_file.input_file_id
                + "/"
                + python_file.python_script_name[0:-3]
                + ".log"
            )
            if not os.path.isfile(log_path):
                print("ERROR5")
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="There is no error log file!",
                )
            return FileResponse(
                log_path,
                media_type="text/plain",
                filename=python_file.python_script_name[0:-3] + ".log",
            )
    # if the project has no model files run simple script
    else:
        try:
            # run the project
            output_file_path = run_simple_script(
                db,
                project_id,
                python_file,
                input_file,
                project.output_type,
                run_history_id,
            )
            # check if result file exists
            print("output file path hereeee:" + output_file_path + project.output_type)
            if not os.path.isfile(output_file_path + project.output_type):
                print("ERROR1")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="There is no output file!",
                )
            """ if project.output_type == ".nii.gz":
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type="application/gzip",
                    filename="result_"
                    + input_file_name_no_extension
                    + project.output_type,
                )
            elif project.output_type == ".csv":
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type="text/csv",
                    filename="result_"
                    + input_file_name_no_extension
                    + project.output_type,
                )
            elif project.output_type == ".png":
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type="image/png",
                    filename="result_"
                    + input_file_name_no_extension
                    + project.output_type,
                )
            elif project.output_type == ".wav":
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type="audio/wav",
                    filename="result_"
                    + input_file_name_no_extension
                    + project.output_type,
                ) """
            media_type_dict = {
                ".nii.gz": ("application/gzip", ".nii.gz"),
                ".csv": ("text/csv", ".csv"),
                ".png": ("image/png", ".png"),
                ".wav": ("audio/wav", ".wav"),
            }

            if project.output_type in media_type_dict:
                media_type, file_ext = media_type_dict[project.output_type]
                return FileResponse(
                    output_file_path + project.output_type,
                    media_type=media_type,
                    filename="result_" + input_file_name_no_extension + file_ext,
                )
        except:
            log_path = (
                "./outputfiles/"
                + input_file.input_file_id
                + "/"
                + python_file.python_script_name[0:-3]
                + ".log"
            )
            if not os.path.isfile(log_path):
                print("ERROR2")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="There is no error log file!",
                )
            return FileResponse(
                log_path,
                media_type="text/plain",
                filename=python_file.python_script_name[0:-3] + ".log",
            )


def check_python_files(project_id: str, db: Session):
    project = (
        db.query(models.Project).filter(models.Project.project_id == project_id).first()
    )
    name_path = (
        db.query(models.Project)
        .filter(models.Project.project_id == project_id)
        .with_entities(
            models.Project.python_script_name, models.Project.python_script_path
        )
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} was not found!",
        )
    if project.python_script_path == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} does not have a python script!",
        )
    file_exists = os.path.isfile(project.python_script_path)
    return name_path


def run_script(
    db: Session,
    project_id: str,
    python_file: dict,
    model_files: dict,
    input_file: dict,
    output_type: str,
    run_history_id: int,
):
    python_script_name = python_file.python_script_name[0:-3]
    input_file_name = input_file.name
    input_file_name_no_extension = input_file_name.split(".")[0]
    print("input_file_name_no_extension: ", input_file_name_no_extension)
    input_file_path = input_file.path
    input_directory_path = input_file_path.replace(input_file_name, "")
    # make output directory
    os.makedirs("./outputfiles/" + input_file.input_file_id, exist_ok=True)

    output_file_id = input_file.input_file_id
    output_directory_path = "./outputfiles/" + input_file.input_file_id + "/"
    output_file_name = "result_" + input_file_name_no_extension
    print("output_file_name: ", output_file_name)
    path = "./modelfiles/" + project_id

    # python_script_name = db.query(models.Project).where(models.Project.project_id == project_id).first().python_script_name[0:-3]
    is_directory = os.path.isdir(path)
    if not is_directory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} has no file directory!",
        )
    # add folder path to sys
    sys.path.append(path)
    # import the module
    script = importlib.import_module(python_script_name)
    # run "load_models" and "run"
    try:
        logname = output_directory_path + python_script_name + ".log"
        print("LOGNAME: ", logname)
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filename=logname)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(formatter)
        log.addHandler(fh)
        log.info("-------Start--------")
        load_models = script.load_models(model_files)
        run_script = script.run(
            input_file_path, output_file_name, output_directory_path
        )
        print("LOAD MODELS:", load_models)
        log.error(f"LOAD MODELS: {load_models}")
        print("RUN SCRIPT:", run_script)
        log.error(f"RUN SCRIPT: {run_script}")

        if not os.path.isfile(output_directory_path + output_file_name + output_type):
            log.error(
                f"Output file does not exist or output type is not {output_type}!"
            )

    except:
        error = log.exception("run_script errors:")
        print("RUN SCRIPT ERROR:", error)

    log.info("-------End--------")
    log.removeHandler(fh)
    del log, fh

    # add the output file information to the database
    files.create_output_file_entry(
        db,
        output_file_id,
        output_file_name + output_type,
        output_directory_path + output_file_name + output_type,
    )

    # add the output file information to the run history table
    runhistory.update_output(db, run_history_id, output_file_id)

    return output_directory_path + output_file_name


def run_simple_script(
    db: Session,
    project_id: str,
    python_file: dict,
    input_file: dict,
    output_type: str,
    run_history_id: int,
):
    python_script_name = python_file.python_script_name[0:-3]
    input_file_name = input_file.name
    input_file_name_no_extension = input_file_name.split(".")[0]
    print("input_file_name_no_extension: ", input_file_name_no_extension)
    input_file_path = input_file.path
    input_directory_path = input_file_path.replace(input_file_name, "")
    # make output directory
    os.makedirs("./outputfiles/" + input_file.input_file_id, exist_ok=True)
    output_file_id = input_file.input_file_id
    output_directory_path = "./outputfiles/" + input_file.input_file_id + "/"
    output_file_name = "result_" + input_file_name_no_extension
    print("output_file_name: ", output_file_name)
    path = "./modelfiles/" + project_id
    is_directory = os.path.isdir(path)
    if not is_directory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} has no file directory!",
        )
    # add folder path to sys
    sys.path.append(path)
    # import the module
    script = importlib.import_module(python_script_name)
    # run "load_models" and "run"
    try:
        logname = output_directory_path + python_script_name + ".log"
        logname = output_directory_path + python_script_name + ".log"
        print("LOGNAME: ", logname)
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filename=logname)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(formatter)
        log.addHandler(fh)
        log.info("-------Start--------")
        run_script = script.run(
            input_file_path, output_file_name, output_directory_path
        )
        print("RUN SCRIPT:", run_script)
        log.error(f"RUN SCRIPT: {run_script}")

        if not os.path.isfile(output_directory_path + output_file_name + output_type):
            log.error(
                f"Output file does not exist or output type is not {output_type}!"
            )

    except:
        error = logging.exception("run_simple_script errors:")
        print(error)

    log.info("-------End--------")
    log.removeHandler(fh)
    del log, fh

    # add the output file information to the database
    files.create_output_file_entry(
        db,
        output_file_id,
        output_file_name + output_type,
        output_directory_path + output_file_name + output_type,
    )

    # add the output file information to the run history table
    runhistory.update_output(db, run_history_id, output_file_id)

    return output_directory_path + output_file_name


# delete project from database
# admin can delete project
# the owner can delete project
def delete(user_email: str, user_role: UserRole, project_id: str, db: Session):
    # get current user id
    user_id = user.get_by_email(user_email, db).user_id
    # check permissions
    # admin can delete any project
    # user owner can delete project
    if not (user_role == "admin") or (userproject.check_owner(user_id, project_id, db)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with id {user_id} is not authorized to delete project with id {project_id}!",
        )
    # check if the project exists
    get_by_id(project_id, db)
    # delete project from database
    project = db.query(models.Project).filter(models.Project.project_id == project_id)
    if not project.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found!",
        )
    try:
        project.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} error deleting from database!",
        )
    # delete from UserProject List
    # not needed because its deleted by cascade
    # userproject.delete(owner_id, project_id, db)
    # deleter from ModelFile table
    # not needed because its deleted by cascade
    # files.delete_model_files(project_id, db)

    # delete project folder from filesystem
    path = "./modelfiles/" + project_id
    if not os.path.isdir(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} has no file directory!",
        )
    try:
        shutil.rmtree(path)
    except:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"Project with id number {project_id} has no directory in the filesystem!",
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"The Project id {project_id} was successfully deleted.",
    )


""" def delete_admin(user_email: str, project_id: str, db: Session):
    # check if admin
    user.is_admin(user_email, db)
    # check if the project exists
    get_by_id(project_id, db)
    # delete project from database
    project = db.query(models.Project).filter(models.Project.project_id == project_id)
    if not project.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found!",
        )
    try:
        project.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} error deleting from database!",
        )
    # delete from UserProject List
    # not needed because its deleted by cascade
    # userproject.delete(owner_id, project_id, db)
    # deleter from ModelFile table
    # not needed because its deleted by cascade
    # files.delete_model_files(project_id, db)
    # delete project folder from filesystem
    path = "./modelfiles/" + project_id
    if not os.path.isdir(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} has no file directory!",
        )
    try:
        shutil.rmtree(path)
    except:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"Project with id number {project_id} has no directory in the filesystem!",
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"The Project id {project_id} was successfully deleted.",
    ) """


# update project by id
def update_by_id(
    db: Session,
    user_email: str,
    user_role: UserRole,
    project_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    input_type: Optional[str] = None,
    output_type: Optional[str] = None,
    is_private: Optional[bool] = None,
):
    # check if "user" is owner
    if user_role == UserRole.user:
        is_owner = userproject.is_owner_bool(user_email, project_id, db)
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {user_email} is not authorized to update Project {project_id}!",
            )
    # check if project exists
    project = get_query_by_id(project_id, db)
    # check if all request fields are empty or null
    try:
        updates = {}
        if title:
            updates["title"] = title
        if description:
            updates["description"] = description
        if input_type:
            updates["input_type"] = input_type
        if output_type:
            updates["output_type"] = output_type
        if is_private is not None:
            updates["is_private"] = is_private
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request Project update fields are all empty!",
            )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating project information: {str(e)}",
        )

    # update project in database
    # NOT TESTED
    try:
        updates["last_updated"] = datetime.now()
        project.update(updates)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Project with id: {project_id} error updating database by User with email: {user_email}! {str(e)}",
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"Project with id: {project_id} was successfully updated by User with email: {user_email}.",
    )
