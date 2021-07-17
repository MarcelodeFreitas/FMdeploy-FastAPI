from fastapi import APIRouter, status, Depends
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import userai

router = APIRouter(
    prefix="/userai",
    tags=['User AI']
)

#UserAi
@router.post("/check_access", status_code = status.HTTP_200_OK, response_model=schemas.UserAIList)
async def check_access_to_ai_model(request: schemas.UserAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userai.check_access_ai_exception(request.user_id, request.ai_id, db)

@router.post("/check_access/bool", status_code = status.HTTP_200_OK, response_model=schemas.Owner)
async def check_access_to_ai_model_boolean(request: schemas.UserAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return {"owner": userai.check_access_ai(request.user_id, request.ai_id, db)}

@router.post("/owner", status_code = status.HTTP_200_OK, response_model=schemas.Owner)
async def check_if_owner(request: schemas.UserAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userai.check_owner(request.user_id, request.ai_id, db)

@router.get("/owned_list/{user_id}", status_code = status.HTTP_200_OK)
async def get_list_of_AImodels_owned_by_user(user_id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userai.user_owned_ai_list(user_id, db)

@router.post("/share", status_code = status.HTTP_200_OK, response_model=schemas.UserAIList)
async def get_list_of_AImodels_owned_by_user(request: schemas.ShareAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userai.user_share_ai(request.user_id_sharer, request.user_id_beneficiary, request.ai_id, db)

@router.post("/is_shared", status_code = status.HTTP_200_OK)
async def check_if_AImodel_is_shared_with_user(request: schemas.UserAI, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userai.check_shared(request.user_id, request.ai_id, db)

@router.get("/shared_list/{user_id}", status_code = status.HTTP_200_OK)
async def get_list_of_AImodels_shared_with_user(user_id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userai.user_shared_ai_list(user_id, db)