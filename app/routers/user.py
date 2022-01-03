from fastapi import APIRouter, status, Depends
from .. import schemas, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import user

router = APIRouter(
    prefix="/user",
    tags=['User']
)

#check if the current user is an admin
@router.get('/is_admin', status_code = status.HTTP_200_OK,  response_model=schemas.ShowUserAdmin)
def check_if_current_user_is_admin(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.get_admin(get_current_user, db)

#get all users
@router.get('/admin', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowUserToAdmin])
def get_all_users(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.get_all(get_current_user, db)

#create admin
@router.post('/admin', status_code = status.HTTP_201_CREATED, response_model=schemas.ShowUserAdmin)
def create_administrator(request: schemas.CreateUser, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.create_admin(get_current_user, request.name, request.email, request.password, db)

#update current user
#dont forget to require new login if password is updated
@router.put('', status_code = status.HTTP_202_ACCEPTED)
def update_current_user(request: schemas.UpdateUser, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.update(get_current_user, request.new_name, request.new_email, db)

#admin update user from email
@router.put('/admin', status_code = status.HTTP_202_ACCEPTED)
def update_user_admin(request: schemas.UpdateUserAdmin, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.update_by_email(get_current_user, request.current_email, request.new_name, request.new_email, db)

#create user
@router.post('', status_code = status.HTTP_201_CREATED, response_model=schemas.ShowUser)
def create_user(request: schemas.CreateUser, db: Session = Depends(get_db)):
    return user.create(request.name, request.email, request.password, db)

#get user by id
@router.get('/admin/id/{user_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowUserAdmin)
def get_user_by_id(user_id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.get_by_id_exposed(get_current_user, user_id, db)

#get current user
@router.get('/current', status_code = status.HTTP_200_OK, response_model=schemas.ShowUser)
def get_current_user(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.get_by_email(get_current_user, db)

#delete current user account
@router.delete('/current', status_code = status.HTTP_200_OK)
def delete_current_user_account(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.delete_account_by_email(get_current_user, db)

#delete user by id for admin
@router.delete('/admin/{user_id}', status_code = status.HTTP_200_OK)
def delete_user_by_id_admin(user_id, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.delete_user_by_id_exposed(get_current_user, user_id, db)

#delete user by email for admin
#CREATE
""" @router.delete('/admin/{user_email}', status_code = status.HTTP_200_OK)
def delete_user_by_email(user_email, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.delete_user_by_email_exposed(get_current_user, user_email, db) """
    
#delete user account by email for admin
#CREATE
""" @router.delete('/admin/{user_email}', status_code = status.HTTP_200_OK)
def delete_user_account_by_email(user_email, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.delete_account_by_email_exposed(get_current_user, user_email, db) """
    
#get user by email
@router.get('/admin/email/{email}', status_code = status.HTTP_200_OK, response_model=schemas.ShowUserToAdmin)
def get_user_by_email_admin(email, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.get_by_email_exposed(get_current_user, email, db)