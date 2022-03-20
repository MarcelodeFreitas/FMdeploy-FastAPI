from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import models, hashing
from . import project

#get user by id for internal use
def get_by_id(user_id: int, db: Session):
    #get user by id
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number: {user_id} was not found!")
    return user

# get user by id for external use by admin
def get_by_id_exposed(user_email: str, user_id: int, db: Session):
    #check if admin
    is_admin(user_email, db)
    #get user by id
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number: {user_id} was not found!")
    return user

# get user query by id needed for updates or deletes in the database
def get_user_query_by_id(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number: {user_id} was not found!")
    return user

#create a user in the database
def create(name: str, email: str, password: str, db: Session):
    new_user = models.User(name=name, email=email, password=hashing.Hash.bcrypt(password))
    try: 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
        detail=f"Email: {email}, is already registered!")
    return new_user

#create admin for use by admins only
def create_admin(user_email: str, name: str, email: str, password: str, db: Session):
    #check if admin
    is_admin(user_email, db)
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

#get all the user in the database for admins
def get_all(user_email: str, db: Session):
    #check if admin
    is_admin(user_email, db)
    #get all users
    user_list = db.query(models.User).all()
    if not user_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"No users found in database!")
    return user_list

#get user by email for external use by admin
def get_by_email_exposed(user_email: str, email: str, db: Session):
    #check if admin
    is_admin(user_email, db)
    #get user by email
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with email: {email} was not found!")
    return user

#get user by email for internal use
def get_by_email(email: str, db: Session):
    #get user by email
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with email: {email} was not found!")
    return user

#get user query by email needed for updates or deletes in the database
def get_user_query_by_email(user_email: str, db: Session):
    user = db.query(models.User).filter(models.User.email == user_email)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with email: {user_email} was not found!")
    return user

#delete user in user table and in userailist table by id
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

#delete user in user table and in userailist table by id for external use by admin
def delete_by_id_exposed(user_email: str, user_id: int, db: Session):
    #check if admin
    is_admin(user_email, db)
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

#delete user in user table and in userailist table by email
def delete_by_email(user_email: str, db: Session):
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
    detail=f"User with email: {user_email} was successfully deleted.")
    
#delete user in user table and in userailist table by email for external use by admin
def delete_by_email_exposed(current_user_email: str, user_email: str, db: Session):
    #check if admin
    is_admin(current_user_email, db)
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
    detail=f"User with email: {user_email} was successfully deleted.")  

#delete current user, all models and modelfiles
#delete user account
def delete_current_account(current_user_email: str, db: Session):
    #check if user exists
    user = get_by_email(current_user_email, db)
    user_id = user.user_id
    try:
        #list project
        project_list = db.query(models.UserProject).where(models.UserProject.fk_user_id == user_id).where(models.UserProject.owner == True).all()
        #delete all Project owned by the user
        if len(project_list) > 0:
            for project_model in project_list:
                project.delete(current_user_email, project_model.fk_project_id, db)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Error deleting Project and files for user with email: {current_user_email} !")
    #delete user from user and userailist tables
    delete_by_email(current_user_email, db)
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"User account successfuly deleted!")
    
#update user email or user name by id
def update_by_id(user_id: int, user_email: str, user_name: str, db: Session):
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

#update user email or user name by email
def update_by_email(user_email: str, new_name: str, new_email: str, new_password: str, db: Session):
    print("NAME: ", new_name, "EMAIL: ", new_email, "PASSWORD: ", new_password)
    #check if user exists
    user = get_user_query_by_email(user_email, db)
    #check what data has been provided in the request
    if (new_email == "" or new_email == None) and (new_name == "" or new_name == None) and (new_password == "" or new_password == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Update fields are empty!")
    #if empty keep previous data
    
    if new_email != "" and new_email != None:
        user.update({'email': new_email})
    if new_name != "" and new_name != None:
        user.update({'name': new_name})
    if new_password != "" and new_password != None:
        user.update({'password': hashing.Hash.bcrypt(new_password)})
    db.commit()
    """ except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
        detail=f"Email: {user_email}, is already registered!") """
    return HTTPException(status_code=status.HTTP_200_OK, 
    detail=f"User data was successfully updated!")

#get admin if is admin else http exception
def is_admin(email: str, db):
    #check user exists
    user = get_by_email(email, db)
    #check if it is an admin
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
         detail=f"User with email: {email} is not an admin!")
    return user

#get admin boolean
def is_admin_bool(email: str, db:Session):
    user = get_by_email(email, db)
    return user.is_admin