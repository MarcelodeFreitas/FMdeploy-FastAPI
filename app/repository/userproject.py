from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .. import models
from . import project, user, userproject
from .user import UserRole


def check_access_exception(user_id: int, project_id: str, db):
    entry = (
        db.query(models.UserProject)
        .where(models.UserProject.fk_user_id == user_id)
        .where(models.UserProject.fk_project_id == project_id)
        .first()
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} has no access to Project id {project_id}!",
        )
    return entry


def check_access(user_id: int, project_id: str, db):
    entry = (
        db.query(models.UserProject)
        .where(models.UserProject.fk_user_id == user_id)
        .where(models.UserProject.fk_project_id == project_id)
        .first()
    )
    if not entry:
        return False
    return True


def check_owner(user_id: int, project_id: str, db):
    entry = (
        db.query(models.UserProject)
        .where(models.UserProject.fk_user_id == user_id)
        .where(models.UserProject.fk_project_id == project_id)
        .with_entities(models.UserProject.owner)
        .first()
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User id: {user_id}, project id: {project_id} is not the owner!",
        )
    return entry


def check_owner_exposed(user_email: str, project_id: str, db):
    # check if project exists
    project.get_by_id(project_id, db)
    user_id = user.get_by_email(user_email, db).user_id
    entry = (
        db.query(models.UserProject)
        .where(models.UserProject.fk_user_id == user_id)
        .where(models.UserProject.fk_project_id == project_id)
        .with_entities(models.UserProject.owner)
        .first()
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User: {user_email}, project id: {project_id} is not the owner!",
        )
    return entry


def get_owner(user_email: str, project_id: str, db):
    # get user id from user email
    user_id = user.get_by_email(user_email, db).user_id
    # check if the user has access to the projects
    check_access_exception(user_id, project_id, db)
    user_query = (
        db.query(models.User)
        .where(
            and_(
                models.UserProject.fk_project_id == project_id,
                models.UserProject.owner == True,
            )
        )
        .outerjoin(models.UserProject)
        .with_entities(models.User.name, models.User.email)
        .first()
    )
    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error getting owner for project '{project_id}'!",
        )
    return user_query


def is_owner_bool(user_email: str, project_id: str, db):
    user_id = user.get_by_email(user_email, db).user_id
    user_project = (
        db.query(models.UserProject)
        .where(models.UserProject.fk_user_id == user_id)
        .where(models.UserProject.fk_project_id == project_id)
        .with_entities(models.UserProject.owner)
        .first()
    )
    if not user_project:
        return False
    return user_project.owner


def delete(user_id: int, project_id: str, db: Session):
    # entry = db.query(models.UserProject).where(models.UserProject.fk_user_id == user_id).where(models.UserProject.fk_project_id == project_id)
    # ajusted to delete the entry that identifies shared models, models that are deleted cant remain shared
    entry = db.query(models.UserProject).where(
        models.UserProject.fk_project_id == project_id
    )
    if not entry.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User id: {user_id}, project id: {project_id} not found in database!",
        )
    try:
        entry.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User id: {user_id}, project id: {project_id} error deleting from database!",
        )
    return True


def owned(current_user_email: str, db: Session):
    # get the user_id from user_email
    user_id = user.get_by_email(current_user_email, db).user_id
    # get entries where user is the owner from UserProject
    userproject = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.UserProject.fk_user_id == user_id)
        .where(models.UserProject.owner == True)
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.created_in,
            models.Project.title,
            models.Project.project_id,
            models.Project.description,
            models.Project.input_type,
            models.Project.output_type,
            models.Project.is_private,
            models.User.name,
        )
        .all()
    )
    if not userproject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {current_user_email}, does not own any Project!",
        )
    return userproject


def share(user_id_sharer: int, user_id_beneficiary: int, project_id: str, db: Session):
    # check if user is the owner
    check_owner(user_id_sharer, project_id, db)
    # check the user exists
    user.get_by_id(user_id_sharer, db)
    # check user beneficiary exists
    user.get_by_id(user_id_beneficiary, db)
    # check if the project exists
    project.get_by_id(project_id, db)
    # check if it is already shared with this user
    check_shared(user_id_beneficiary, project_id, db)
    # create UserProject entry where owner=false and beneficiary=true
    new_entry = models.UserProject(
        fk_user_id=user_id_beneficiary, fk_project_id=project_id, owner=False
    )
    try:
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project id: {project_id}, user id sharer: {user_id_sharer}, user id beneficiary: {user_id_beneficiary} error sharing Project!",
        )
    return new_entry


# share a project with another user by email
def share_exposed(
    current_user_email: str,
    user_role: UserRole,
    beneficiary_email: str,
    project_id: str,
    db: Session,
):
    # check if current_user_email is the same as beneficiary_email
    if current_user_email == beneficiary_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"A project can't be shared with the owner",
        )
    # check if the project exists
    project_object = project.get_by_id(project_id, db)
    # check if the project is private
    if not (project_object.is_private):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This Project is already public",
        )
    # check permissions
    # check if owner or admin
    if not (
        (user_role == "admin")
        or (userproject.is_owner_bool(current_user_email, project_id, db))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with email: {current_user_email} does not have permissions to share Project id: {project_id}!",
        )
    # check the user exists
    user_id_sharer = user.get_by_email(current_user_email, db).user_id
    # check user beneficiary exists
    user_id_beneficiary = user.get_by_email(beneficiary_email, db).user_id
    # check if it is already shared with this user
    check_shared(user_id_beneficiary, project_id, db)
    # create UserProject entry where owner=false and beneficiary=true
    new_entry = models.UserProject(
        fk_user_id=user_id_beneficiary, fk_project_id=project_id, owner=False
    )
    try:
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project id: {project_id}, sharer: {current_user_email}, user beneficiary: {beneficiary_email} error sharing Project!",
        )
    return f"Project id:  {project_id}, shared with {beneficiary_email}"


# cancel a project share with another user by email
def user_cancel_share(
    current_user_email: str,
    user_role: UserRole,
    beneficiary_email: str,
    project_id: str,
    db: Session,
):
    # check if the project exists
    project_object = project.get_by_id(project_id, db)
    if not (project_object.is_private):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This Project is already public",
        )
    # check permissions
    # check if owner or admin
    if not (
        (user_role == "admin")
        or (userproject.is_owner_bool(current_user_email, project_id, db))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with email: {current_user_email} does not have permissions to share Project id: {project_id}!",
        )
    # check user beneficiary exists
    user_id_beneficiary = user.get_by_email(beneficiary_email, db).user_id
    # check if it is shared with this user
    userproject_entry = check_shared_entry(user_id_beneficiary, project_id, db)
    # deleting entry from userproject list
    try:
        userproject_entry.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project id: {project_id}, sharer: {current_user_email}, user beneficiary: {beneficiary_email} error canceling share Project!",
        )
    return f"Project id:  {project_id}, not shared with {beneficiary_email}"


def check_shared(user_id_beneficiary: int, project_id: str, db: Session):
    entry = (
        db.query(models.UserProject)
        .where(
            and_(
                models.UserProject.fk_project_id == project_id,
                models.UserProject.fk_user_id == user_id_beneficiary,
                models.UserProject.owner == False,
            )
        )
        .first()
    )
    if not entry:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project id: {project_id} not shared with user!",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Project id: {project_id} already shared with user!",
    )


def check_shared_entry(user_id_beneficiary: int, project_id: str, db: Session):
    print(user_id_beneficiary)
    entry = db.query(models.UserProject).where(
        and_(
            models.UserProject.fk_project_id == project_id,
            models.UserProject.fk_user_id == user_id_beneficiary,
            models.UserProject.owner == False,
        )
    )
    if not entry.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project id: {project_id} not shared with user {user_id_beneficiary}!",
        )
    else:
        return entry


def shared_projects(user_id: int, db: Session):
    # check the user exists
    user.get_by_id(user_id, db)
    # get entries where user is the owner from UserProject
    userproject = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.UserProject.fk_user_id == user_id)
        .where(models.UserProject.owner == False)
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .all()
    )
    if not userproject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User id: {user_id}, does have shared Project in the database!",
        )
    return userproject


def shared_projects_exposed(current_user_email: str, db: Session):
    # get the user id
    user_id = user.get_by_email(current_user_email, db).user_id
    # get entries where user is the beneficiary from UserProject
    userproject = (
        db.query(models.UserProject, models.Project, models.User)
        .where(models.UserProject.fk_user_id == user_id)
        .where(models.UserProject.owner == False)
        .outerjoin(models.Project)
        .outerjoin(models.User)
        .with_entities(
            models.Project.project_id,
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
    if not userproject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {current_user_email}, does not have any shared Project!",
        )
    return userproject


def create_project_user_entry(user_id: str, project_id: int, db: Session):
    new_entry = models.UserProject(
        fk_user_id=user_id, fk_project_id=project_id, owner=True
    )
    try:
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id number {project_id} error creating AIUserList table entry!",
        )
    return new_entry


# get the list of user that a certain Project has been shared with
def check_beneficiaries(
    project_id: str, current_user_email: str, user_role: UserRole, db: Session
):
    # check credentials
    # check if owner or admin
    if not (
        (user_role == "admin") or (is_owner_bool(current_user_email, project_id, db))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with email: {current_user_email} does not have permissions to check beneficiaries of Project id: {project_id}!",
        )
    userproject = (
        db.query(models.UserProject, models.User)
        .where(models.UserProject.fk_project_id == project_id)
        .where(models.UserProject.owner == False)
        .outerjoin(models.User)
        .with_entities(models.User.name, models.User.email)
        .all()
    )
    if not userproject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The Project id: {project_id} has not been shared!",
        )
    return userproject
