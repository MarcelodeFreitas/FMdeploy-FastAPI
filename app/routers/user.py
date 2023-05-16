from fastapi import APIRouter, status, Depends
from .. import schemas, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import user

router = APIRouter(prefix="/user", tags=["User"])


# get role for the current user
# authorization: any + login required
@router.get("/role", status_code=status.HTTP_200_OK)
def get_current_user_role(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return current_user.role


# get all users
# authorization: admin
@router.get(
    "/all", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowUserAdmin]
)
def get_all_users_for_admin(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_admin),
):
    return user.get_all(db)


# get current user
# authorization: any + login required
@router.get("", status_code=status.HTTP_200_OK, response_model=schemas.ShowUser)
def get_current_user(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return user.get_by_email(current_user.email, db)


# update current user information (name, email, password)
# dont forget to require new login
# authorization: any + login required
@router.put("", status_code=status.HTTP_202_ACCEPTED)
def update_current_user(
    request: schemas.UpdateUser,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return user.update_by_email(
        current_user.email,
        request.new_name,
        request.new_email,
        request.new_password,
        db,
    )


# create user with role default "guest"
# authorization: any + no login required
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.ShowUser)
def create_user_with_role_guest(
    request: schemas.CreateUser, db: Session = Depends(get_db)
):
    return user.create(request.name, request.email, request.password, db)


# delete current user but leave all models and files
# only deletes user from database
# authorization: any + login required
@router.delete("", status_code=status.HTTP_200_OK)
def delete_current_user_from_database(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return user.delete_by_email(current_user.email, db)


# update current user information (name, email, password and role)
# authorization: admin
@router.put(
    "/admin", status_code=status.HTTP_200_OK, response_model=schemas.ShowUserAdmin
)
def update_user(
    request: schemas.UpdateUserAdmin,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_admin),
):
    return user.update_by_email_with_role(
        db,
        request.user_email,
        request.new_name,
        request.new_email,
        request.new_password,
        request.new_role,
    )


# create user with any role
# authorization: admin
@router.post(
    "/admin", status_code=status.HTTP_201_CREATED, response_model=schemas.ShowUserAdmin
)
def create_user_with_any_role(
    request: schemas.CreateUserAdmin,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_admin),
):
    return user.create_with_role(
        db, request.name, request.email, request.password, request.role
    )


# bet user by id
# authorization: admin
@router.get(
    "/admin/id/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ShowUserAdmin,
)
def get_user_by_id(
    user_id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_admin),
):
    return user.get_by_id(user_id, db)


# delete user by id
# authorization: admin
@router.delete("/admin/id/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_by_id(
    user_id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_admin),
):
    return user.delete_by_id(user_id, db)


# delete user by email
# authorization: admin
@router.delete("/admin/email/{user_email}", status_code=status.HTTP_200_OK)
def delete_user_by_email(
    user_email,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_admin),
):
    return user.delete_by_email(user_email, db)


# delete current user account, delete all models and files, shared models will also be deleted
# authorization: any + login required
@router.delete("/account", status_code=status.HTTP_200_OK)
def delete_current_user_account(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return user.delete_current_account(current_user.email, db)


# get user by email for admin
# authorization: admin
@router.get(
    "/admin/email/{user_email}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ShowUserAdmin,
)
def get_user_by_email(
    email,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_admin),
):
    return user.get_by_email(email, db)
