from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from . import user
import uuid

print(str(uuid.uuid4()))

def get_all(db: Session):
    ai_list = db.query(models.AI).all()
    return ai_list

def create_ai_entry(ai_id: str, request: schemas.CreateAI, db: Session):
    new_ai = models.AI(ai_id = ai_id, title=request.title, description=request.description, output_type=request.output_type,is_private=request.is_private, created_in=request.created_in)
    db.add(new_ai)
    db.commit()
    db.refresh(new_ai)
    return new_ai

def create_ai_user_list_entry(user_id: str, ai_id: int, db: Session):
    new_ai_user_list = models.UserAIList(fk_user_id=user_id, fk_ai_id=ai_id,owner=True)
    db.add(new_ai_user_list)
    db.commit()
    db.refresh(new_ai_user_list)
    return new_ai_user_list

def create_ai(request: schemas.CreateAI, db: Session):
    ai_id = str(uuid.uuid4())
    user.get_user_by_id(request.user_id, db)
    create_ai_entry(ai_id, request, db)
    create_ai_user_list_entry(request.user_id, ai_id, db)
    return {"ai_id": ai_id}

def get_ai_by_id(ai_id: str, db: Session):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found!")
    return ai


