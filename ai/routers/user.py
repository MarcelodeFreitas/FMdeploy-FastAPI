from fastapi import APIRouter, HTTPException, status, Depends
from .. import schemas, models
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/user",
    tags=['User']
)

#create user
@router.post('/', status_code = status.HTTP_201_CREATED, response_model=schemas.ShowUser)
def create_user(request: schemas.CreateUser, db: Session = Depends(get_db)):
    new_user = models.User(name=request.name, email=request.email, password=request.password)
    try: 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Email is already registered!")
    return new_user

#get all users
@router.get('/', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowUser])
def get_all_users(db: Session = Depends(get_db)):
    user_list = db.query(models.User).all()
    return user_list

#get user model by id
@router.get('/{user_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowUser)
def get_user_by_id(user_id, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number {user_id} was not found!")
    return user

#get user model by email
@router.get('/email/{user_email}', status_code = status.HTTP_200_OK, response_model=schemas.ShowUser)
def get_user_by_email(user_email, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with  {user_email} was not found!")
    return user

#delete user by id
@router.delete('/{user_id}', status_code = status.HTTP_200_OK)
def delete_user(user_id, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found!")
    user.delete(synchronize_session=False)
    db.commit()
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"User id {user_id} was successfully deleted.")

#update user by id
@router.put('/{user_id}', status_code = status.HTTP_202_ACCEPTED, response_model=schemas.ShowUser)
def update_user_by_id(user_id, request: schemas.UpdateUser, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found!")
    if user.first().name == "" or user.first().name == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} name can't be empty string or None!")
    try:
        user.update(request.dict())
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Email is already registered!")
    return user.first()
