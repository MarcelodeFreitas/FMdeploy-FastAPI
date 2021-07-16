from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, hashing

def get_user_by_id(user_id: int, db: Session):
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

def get_all_users(db: Session):
    user_list = db.query(models.User).all()
    if not user_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"No users found in database!")
    return user_list

def get_user_by_email(user_email: str, db: Session):
    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with email: {user_email} was not found!")
    return user

def get_user_query_by_email(user_email: str, db: Session):
    user = db.query(models.User).filter(models.User.email == user_email)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with email: {user_email} was not found!")
    return user

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

def update_user_by_id(user_id: int, user_email: str, user_name: str, db: Session):
    print(user_email, user_name)
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