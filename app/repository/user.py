from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import models, hashing
from . import project
from enum import Enum
from typing import Optional


# get user role
def get_role(db: Session, email: str):
    # get user
    user = get_by_email(email, db)
    # return role
    return user.role


# get user by id
def get_by_id(user_id: int, db: Session):
    # get user by id from the database by id
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    # raise exception if user not found in database user table
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id number: {user_id} was not found!",
        )
    return user


# get user query by id needed for updates or deletes in the database
# returns user instead of user.first()
def get_user_query_by_id(user_id: int, db: Session):
    # get user from the database by id
    user = db.query(models.User).filter(models.User.user_id == user_id)
    # raise exception if user not found in database user table
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id number: {user_id} was not found!",
        )
    return user


# create a user in the database with default role "guest"
# since role is not provided it defaults to "guest"
def create(name: str, email: str, password: str, db: Session):
    # create a new user
    new_user = models.User(
        name=name, email=email, password=hashing.Hash.bcrypt(password)
    )
    try:
        # add the new user to the database
        db.add(new_user)
        db.commit()
        # refresh in order to return updated user information
        # not sure if refresh is needed here
        db.refresh(new_user)
    except:
        # raise exception if there is an error adding the user to the database
        # the only case I foresee is if the email is already registered
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email: {email}, is already registered!",
        )
        # return updated user information
    return new_user


# create a user with any role
def create_with_role(db: Session, name: str, email: str, password: str, role: str):
    new_user = models.User(
        name=name, email=email, password=hashing.Hash.bcrypt(password), role=role
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email: {email}, is already registered!",
        )
    return new_user


# get a list of all the users in the database
def get_all(db: Session):
    # get all users
    user_list = db.query(models.User).all()
    # raise exception if no users found in database
    if not user_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found in database!"
        )
    return user_list


# get user by email
def get_by_email(email: str, db: Session):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email: {email} not found!",
        )
    return user


# get user query by email needed for updates or deletes in the database
def get_user_query_by_email(user_email: str, db: Session):
    # returns user instead of user.first()
    user = db.query(models.User).filter(models.User.email == user_email)
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email: {user_email} was not found!",
        )
    return user


# delete user in user table and in userproject table by id
# confirm if it is actually deleting from userproject table!!!!!!!
def delete_by_id(user_id: int, db: Session):
    # get the user object by id
    user = get_user_query_by_id(user_id, db)
    # delete user
    try:
        user.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error deleting user with id: {user_id} from database!",
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"User with id: {user_id} was successfully deleted.",
    )


# delete user in user table and in userproject table by email
# confirm if it is actually deleting from userproject table!!!!!!!
def delete_by_email(user_email: str, db: Session):
    # get the user object using the email
    user = get_user_query_by_email(user_email, db)
    # delete user
    try:
        user.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error deleting user with email: {user_email} from database!",
        )
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"User with email: {user_email} was successfully deleted.",
    )


# delete current user, all models and modelfiles
# delete user account
def delete_current_account(current_user_email: str, db: Session):
    # get user by email
    user = get_by_email(current_user_email, db)
    user_id = user.user_id
    try:
        # list project
        project_list = (
            db.query(models.UserProject)
            .where(models.UserProject.fk_user_id == user_id)
            .where(models.UserProject.owner == True)
            .all()
        )
        # delete all Projects owned by the user
        if len(project_list) > 0:
            for project_model in project_list:
                project.delete(current_user_email, project_model.fk_project_id, db)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error deleting Project and files for user with email: {current_user_email} !",
        )
    # delete user from user and userproject tables
    delete_by_email(current_user_email, db)
    return HTTPException(
        status_code=status.HTTP_200_OK, detail=f"User account successfuly deleted!"
    )


# update current user information (name, email, password) by email
# if email or password is changed then the user should be prompted to login again in the frontend
def update_by_email(
    user_email: str, new_name: str, new_email: str, new_password: str, db: Session
):
    print("NAME: ", new_name, "EMAIL: ", new_email, "PASSWORD: ", new_password)
    # get user by email
    user = get_user_query_by_email(user_email, db)
    # check what data has been provided in the request
    if not new_email and not new_name and not new_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Update fields are all empty!",
        )
    try:
        updates = {}
        # if empty keep previous data
        if new_email:
            updates["email"] = new_email
        if new_name:
            updates["name"] = new_name
        if new_password:
            updates["password"] = hashing.Hash.bcrypt(new_password)
        user.update(updates)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user information: {str(e)}",
        )
    return HTTPException(
        status_code=status.HTTP_200_OK, detail=f"User data was successfully updated!"
    )


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


# update current user information with role (name, email, password, and role) by email
def update_by_email_with_role(
    db: Session,
    current_email: str,
    new_name: str,
    new_email: str,
    new_password: str,
    new_role: Optional[UserRole] = None,
):
    print(
        "NAME: ",
        new_name,
        "EMAIL: ",
        new_email,
        "PASSWORD: ",
        new_password,
        "ROLE: ",
        new_role,
    )
    # get user by email
    user = get_user_query_by_email(current_email, db)
    # check what data has been provided in the request
    if not new_email and not new_name and not new_password and not new_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Update fields are all empty!",
        )
    try:
        updates = {}
        # if empty keep previous data
        if new_email:
            updates["email"] = new_email
        if new_name:
            updates["name"] = new_name
        if new_password:
            updates["password"] = hashing.Hash.bcrypt(new_password)
        if new_role:
            updates["role"] = new_role
        user.update(updates)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user information: {str(e)}",
        )
    return user.first()
