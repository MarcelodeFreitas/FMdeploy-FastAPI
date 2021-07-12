from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from .. import schemas, models
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import ai, user, userai
import shutil
import os

router = APIRouter(
    prefix="/userai",
    tags=['User AI']
)

#AI

@router.post("/check_access", status_code = status.HTTP_200_OK, response_model=schemas.UserAIList)
async def check_access_to_ai_model(request: schemas.UserAI, db: Session = Depends(get_db)):
    return userai.check_access_ai_exception(request.user_id, request.ai_id, db)

@router.post("/check_access/bool", status_code = status.HTTP_200_OK, response_model=schemas.Owner)
async def check_access_to_ai_model_boolean(request: schemas.UserAI, db: Session = Depends(get_db)):
    return {"owner": userai.check_access_ai(request.user_id, request.ai_id, db)}

@router.post("/owner", status_code = status.HTTP_200_OK, response_model=schemas.Owner)
async def check_if_owner(request: schemas.UserAI, db: Session = Depends(get_db)):
    return userai.check_owner_ai(request.user_id, request.ai_id, db)
