from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .. import schemas, models
from . import user, userproject
from datetime import datetime
from typing import Optional
from .user import UserRole


# get run hitory for current user
def get_current(user_email: str, db: Session):
    # get the user_id from user_email
    user_id = user.get_by_email(user_email, db).user_id
    # list entries where user_id is a fk_user_id in the run history table
    run_history = (
        db.query(
            models.RunHistory,
            models.User,
            models.Project,
            models.InputFile,
            models.OutputFile,
        )
        .where(models.RunHistory.fk_user_id == user_id)
        .outerjoin(models.User)
        .outerjoin(models.Project)
        .outerjoin(models.InputFile)
        .outerjoin(models.OutputFile)
        .with_entities(
            models.RunHistory.run_history_id,
            models.RunHistory.flagged,
            models.RunHistory.flag_description,
            models.RunHistory.timestamp,
            models.RunHistory.fk_input_file_id,
            models.RunHistory.fk_output_file_id,
            models.User.email,
            models.User.name,
            models.Project.project_id,
            models.Project.title,
            models.Project.description,
            models.InputFile.name.label("input_file_name"),
            models.InputFile.path.label("input_file_path"),
            models.OutputFile.name.label("output_file_name"),
            models.OutputFile.path.label("output_file_path"),
        )
        .all()
    )
    if not run_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Run History table is empty!"
        )
    return run_history


# get run history of flagged outputs for a specific project and check if owner
def get_project_flagged_outputs(
    db: Session, user_email: str, user_role: UserRole, project_id: str
):
    """# get user id from user email
    user_id = user.get_by_email(user_email, db).user_id"""
    # check permissions
    # check if owner or admin
    if not (
        (user_role == "admin")
        or (userproject.is_owner_bool(user_email, project_id, db))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with email: {user_email} does not have permissions to view flagged outputs of Project id: {project_id}!",
        )
    # list entries where the
    # project_id is a fk_project_id in the run history table
    # and flagged is True
    # and owner is True
    flagged = (
        db.query(
            models.RunHistory,
            models.User,
            models.Project,
            models.InputFile,
            models.OutputFile,
            models.UserProject,
        )
        .select_from(models.RunHistory)  # Specify the table to join from
        .where(models.RunHistory.fk_project_id == project_id)
        .where(models.RunHistory.flagged == True)
        .outerjoin(models.User)
        .outerjoin(models.Project)
        .outerjoin(models.InputFile)
        .outerjoin(models.OutputFile)
        .with_entities(
            models.RunHistory.run_history_id,
            models.RunHistory.flagged,
            models.RunHistory.flag_description,
            models.RunHistory.timestamp,
            models.RunHistory.fk_input_file_id,
            models.RunHistory.fk_output_file_id,
            models.User.email,
            models.User.name,
            models.Project.project_id,
            models.Project.title,
            models.Project.description,
            models.InputFile.name.label("input_file_name"),
            models.InputFile.path.label("input_file_path"),
            models.OutputFile.name.label("output_file_name"),
            models.OutputFile.path.label("output_file_path"),
        )
        .all()
    )
    if not flagged:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flagged Output table is empty!",
        )
    return flagged


# create an entry in the run history table
def create_entry(
    db: Session,
    fk_user_id: int,
    fk_project_id: str,
    fk_input_file_id: str,
    fk_output_file_id: Optional[str] = None,
    flagged: bool = False,
    flag_description: Optional[str] = None,
):
    new = models.RunHistory(
        fk_user_id=fk_user_id,
        fk_project_id=fk_project_id,
        fk_input_file_id=fk_input_file_id,
        fk_output_file_id=fk_output_file_id,
        flagged=flagged,
        flag_description=flag_description,
        timestamp=datetime.now(),
    )
    try:
        db.add(new)
        db.commit()
        db.refresh(new)
        return new.run_history_id
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {fk_project_id} error creating Run History table entry!",
        )


# get run history entry by id
def get_by_id(db: Session, run_history_id: int):
    # get the run history entry by id
    run_history = (
        db.query(models.RunHistory)
        .where(models.RunHistory.run_history_id == run_history_id)
        .first()
    )
    if not run_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run History entry with id number {run_history_id} not found!",
        )
    return run_history


# get run history entry by output file id
def get_by_output_file_id(db: Session, output_file_id: str):
    # get the run history entry by id
    run_history = (
        db.query(models.RunHistory)
        .where(models.RunHistory.fk_output_file_id == output_file_id)
        .first()
    )
    if not run_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run History entry with output_file_id: {output_file_id} not found!",
        )
    return run_history


# get run history entry by input file id
def get_by_input_file_id(db: Session, input_file_id: str):
    # get the run history entry by id
    run_history = (
        db.query(models.RunHistory)
        .where(models.RunHistory.fk_input_file_id == input_file_id)
        .first()
    )
    if not run_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run History entry with input_file_id: {input_file_id} not found!",
        )
    return run_history


# update fk_output_file_id to run history entry by id
def update_output(db: Session, run_history_id: int, output_file_id: str):
    print("update_output: ", run_history_id, output_file_id)
    # get the run history entry by id
    run_history_entry = get_by_id(db, run_history_id)
    print("run_history_entry: ", run_history_entry)
    # if a request field is empty or null keep the previous value
    if output_file_id == "" or output_file_id == None:
        output_file_id = run_history_entry.first().fk_output_file_id
    # update run history entry in the database
    try:
        # .update() method is not avaiilable for individual model objects
        run_history_entry.fk_output_file_id = output_file_id
        db.commit()
    except Exception as e:
        raise Exception(
            f"Run History with id: {run_history_id} error updating database ! Error message: {str(e)}"
        )
    return f"Run History with id: {run_history_id} was successfully updated."
    """ except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run History with id: {request.run_history_id} error updating database by User with email: {user_email}!",
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"Run History with id: {request.run_history_id} was successfully updated by User with email: {user_email}.",
    ) """


# update flag and flag description to run history entry by id
def flag_by_run_history_id(
    user_email: str, db: Session, request: schemas.RunHistoryFlag
):
    # get the run history entry by id
    run_history_entry = get_by_id(db, request.run_history_id)
    # update run history entry in the database
    try:
        # .update() method is not avaiilable for individual model objects
        run_history_entry.flagged = request.flagged
        run_history_entry.flag_description = request.flag_description
        db.commit()
    except Exception as e:
        raise Exception(
            f"Run History with id: {request.run_history_id} error updating database ! Error message: {str(e)}"
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"Run History with id: {request.run_history_id} was successfully updated by User with email: {user_email}.",
    )


# update flag and flag description to run history entry by output_file_id
def flag_by_output_file_id(
    user_email: str, db: Session, request: schemas.RunHistoryFlagOutput
):
    # get the run history entry by id
    run_history_entry = get_by_output_file_id(db, request.output_file_id)
    # update run history entry in the database
    try:
        # .update() method is not avaiilable for individual model objects
        run_history_entry.flagged = request.flagged
        run_history_entry.flag_description = request.flag_description
        db.commit()
    except Exception as e:
        raise Exception(
            f"Run History with output_file_id: {request.output_file_id} error updating database ! Error message: {str(e)}"
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"Run History with output_file_id: {request.output_file_id} was successfully updated by User with email: {user_email}.",
    )


# update flag and flag description to run history entry by input_file_id
def flag_by_input_file_id(
    user_email: str, db: Session, request: schemas.RunHistoryFlagInput
):
    # get the run history entry by id
    run_history_entry = get_by_input_file_id(db, request.input_file_id)
    # update run history entry in the database
    try:
        # .update() method is not avaiilable for individual model objects
        run_history_entry.flagged = request.flagged
        run_history_entry.flag_description = request.flag_description
        db.commit()
    except Exception as e:
        raise Exception(
            f"Run History with input_file_id: {request.input_file_id} error updating database ! Error message: {str(e)}"
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"Run History with input_file_id: {request.input_file_id} was successfully updated by User with email: {user_email}.",
    )
