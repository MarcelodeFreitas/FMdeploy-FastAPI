from fastapi import APIRouter, status, Depends
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import userproject

router = APIRouter(
    prefix="/userproject",
    tags=['User Project']
)


@router.post("/check_access", status_code = status.HTTP_200_OK, response_model=schemas.UserProject)
def check_access_to_project(request: schemas.UserProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.check_access_exception(request.user_id, request.project_id, db)

@router.post("/check_access/bool", status_code = status.HTTP_200_OK, response_model=schemas.Owner)
def check_access_to_project_boolean(request: schemas.UserProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return {"owner": userproject.check_access(request.user_id, request.project_id, db)}

@router.post("/owner", status_code = status.HTTP_200_OK, response_model=schemas.Owner)
def check_if_owner(request: schemas.UserProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.check_owner(request.user_id, request.project_id, db)

@router.get("/owned_list", status_code = status.HTTP_200_OK)
def get_list_of_projects_owned_by_user(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.owned(get_current_user, db)

@router.post("/share", status_code = status.HTTP_200_OK)
def share_project(request: schemas.ShareProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.share_exposed(get_current_user, request.beneficiary_email, request.project_id, db)

@router.post("/cancel_share", status_code = status.HTTP_200_OK)
def cancel_share_project(request: schemas.ShareProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.user_cancel_share(get_current_user, request.beneficiary_email, request.project_id, db)

@router.post("/is_shared", status_code = status.HTTP_200_OK)
def check_if_project_is_shared_with_user(request: schemas.UserProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.check_shared(request.user_id, request.project_id, db)

@router.get("/shared_list", status_code = status.HTTP_200_OK)
def get_list_of_projects_shared_with_user(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.shared_projects_exposed(get_current_user, db)

@router.get("/beneficiaries/{project_id}", status_code = status.HTTP_200_OK)
def get_list_of_beneficiaries_by_project(project_id: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.check_beneficiaries(project_id, get_current_user, db)

@router.get("/admin/shared_list/{user_id}", status_code = status.HTTP_200_OK)
def get_list_of_projects_shared_with_user_id(user_id: int, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.shared_projects(user_id, db)

@router.get('/test/{project_id}', status_code = status.HTTP_202_ACCEPTED)
def test(project_id:str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return userproject.get_owner(project_id, db)