from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import models, hashing
from . import ai

def get_user_by_id_exposed(user_email: str, user_id: int, db: Session):
    #check if admin
    user_is_admin(user_email, db)
    #get user by id
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number: {user_id} was not found!")
    return user

def get_user_by_id(user_id: int, db: Session):
    #get user by id
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number: {user_id} was not found!")
    return user

def get_user_query_by_id(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number: {user_id} was not found!")
    return user

def create_user(name: str, email: str, password: str, db: Session):
    new_user = models.User(name=name, email=email, password=hashing.Hash.bcrypt(password))
    try: 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
        detail=f"Email: {email}, is already registered!")
    return new_user

def create_admin(user_email: str, name: str, email: str, password: str, db: Session):
    #check if admin
    user_is_admin(user_email, db)
    #create new admin
    new_user = models.User(name=name, email=email, password=hashing.Hash.bcrypt(password), is_admin=True)
    try: 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
        detail=f"Email: {email}, is already registered!")
    return new_user

""" create_admin("admin", "admin@gmail.com", "um.2021", ) """

def get_all_users(user_email: str, db: Session):
    #check if admin
    user_is_admin(user_email, db)
    #get all users
    user_list = db.query(models.User).all()
    if not user_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"No users found in database!")
    return user_list

def get_user_by_email_exposed(user_email: str, email: str, db: Session):
    #check if admin
    user_is_admin(user_email, db)
    #get user by email
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with email: {email} was not found!")
    return user

def get_user_by_email(email: str, db: Session):
    #get user by email
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with email: {email} was not found!")
    return user

def get_user_query_by_email(user_email: str, db: Session):
    user = db.query(models.User).filter(models.User.email == user_email)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with email: {user_email} was not found!")
    return user

def delete_user_by_id_admin(user_email: str, user_id: int, db: Session):
    #check if admin
    user_is_admin(user_email, db)
    #check if user exists
    user = get_user_query_by_id(user_id, db)
    #delete user
    try:
        user.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Error deleting user with id: {user_id} from database!")
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"User with id: {user_id} was successfully deleted.")
    
def delete_user_by_id(user_id: int, db: Session):
    #check if user exists
    user = get_user_query_by_id(user_id, db)
    #delete user
    try:
        user.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Error deleting user with id: {user_id} from database!")
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"User with id: {user_id} was successfully deleted.")
    
def delete_user_by_email(user_email: str, db: Session):
    #check if user exists
    user = get_user_query_by_email(user_email, db)
    #delete user
    try:
        user.delete(synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Error deleting user with email: {user_email} from database!")
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"User with id: {user_email} was successfully deleted.")

#delete current user and all models
def delete_current_user(current_user_email: str, db: Session):
    #check if user exists
    user = get_user_by_email(current_user_email, db)
    user_id = user.user_id
    """ try: """
    #list ai
    ai_list = db.query(models.UserAIList).where(models.UserAIList.fk_user_id == user_id).where(models.UserAIList.owner == True).all()
    #delete all ai models owned by the user
    if len(ai_list) > 0:
        for ai_model in ai_list:
            ai.delete(current_user_email, ai_model.fk_ai_id, db)
    #delete user
    delete_user_by_email(current_user_email, db)
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"User account successfuly deleted!")
    
def update_user_by_id(user_id: int, user_email: str, user_name: str, db: Session):
    #check if user exists
    user = get_user_query_by_id(user_id, db)
    #check what data has been provided in the request
    if (user_email == "" or user_email == None) and (user_name == "" or user_name == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Request user update fields are both empty!")
    if user_email == "" or user_email == None:
        user_email = user.first().email
    if user_name == "" or user_name == None:
        user_name = user.first().name
    #update user in database
    try:
        user.update({'name': user_name})
        user.update({'email': user_email})
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
        detail=f"Email: {user_email}, is already registered!")
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"User with id: {user_id} was successfully updated.")

def update_user_by_email(user_email: str, new_name: str, new_email: str, db: Session):
    #check if user exists
    user = get_user_query_by_email(user_email, db)
    #check what data has been provided in the request
    if (new_email == "" or new_email == None) and (new_name == "" or new_name == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Request user update fields are both empty!")
    #if empty keep previous data
    if new_email == "" or new_email == None:
        new_email = user.first().email
    if new_name == "" or new_name == None:
        new_name = user.first().name
    #update user in database
    try:
        user.update({'name': new_name})
        user.update({'email': new_email})
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
        detail=f"Email: {user_email}, is already registered!")
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"User data was successfully updated.")

def user_is_admin(email: str, db):
    #check user exists
    user = get_user_by_email(email, db)
    #check if it is an admin
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with email: {email} is not an admin!")
    return user

def is_admin_bool(email: str, db:Session):
    user = get_user_by_email(email, db)
    return user.is_admin