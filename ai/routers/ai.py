from fastapi import APIRouter, HTTPException, status, Depends
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import ai

router = APIRouter(
    prefix="/ai",
    tags=['AI models']
)

#create ai model
@router.post('/', status_code = status.HTTP_201_CREATED, response_model=schemas.CreatedAI)
def create_ai(request: schemas.CreateAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.create_ai(request, db)

#create ai model with current user
@router.post('/current', status_code = status.HTTP_201_CREATED, response_model=schemas.CreatedAI)
def create_ai_with_current_user(request: schemas.CreateAICurrent, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.create_ai_current(request, get_current_user, db)

#get all ai models
@router.get('/', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_all_ai(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.get_all(db)

#get all public ai models
@router.get('/public', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_all_public_ai(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.get_all_public(db)

#get public ai models by id
@router.get('/public/{ai_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowAI)
def get_all_public_ai_by_id(ai_id: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.get_public_by_id_exposed(ai_id, db)

#get public ai model by title
@router.get('/public/title/{title}', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_public_ai_by_title(title: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.get_public_by_title_exposed(title, db)

#get ai model by id
@router.get('/{ai_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowAI)
def get_ai_by_id(ai_id: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.get_ai_by_id_exposed(get_current_user, ai_id, db)

#get ai model by title
@router.get('/title/{title}', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_ai_by_title(title: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.get_ai_by_title(title, db)

#delete ai model from database tables and filesystem
@router.delete('/', status_code = status.HTTP_200_OK)
def delete_ai(request: schemas.UserAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return ai.delete(request.user_id, request.ai_id, db)

#run a model by id
@router.post('/run', status_code = status.HTTP_202_ACCEPTED)
async def run_ai(request: schemas.RunAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return await ai.run_ai(request.user_id, request.ai_id, request.input_file_id, db)

@router.put('/{ai_id}', status_code = status.HTTP_202_ACCEPTED, response_model=schemas.ShowAI)
def update_ai_by_id(ai_id, request: schemas.UpdateAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
    if not ai.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
    ai.update(request.dict())
    db.commit()
    return ai.first()