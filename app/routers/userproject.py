from fastapi import APIRouter, status, Depends
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import userproject, runhistory

router = APIRouter(prefix="/userproject", tags=["User Project"])


# check if the current user is the owner of the project by id
# authorization: any + login required
@router.post(
    "/owner/{project_id}", status_code=status.HTTP_200_OK, response_model=schemas.Owner
)
def check_if_owner(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return userproject.check_owner_exposed(current_user.email, project_id, db)


# get the list of projects owned by the user
# authorization: admin or user
@router.get(
    "/owned_list",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ShowProject],
)
def get_list_of_projects_owned_by_user(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return userproject.owned(current_user.email, db)


# share a project with a specific user by providing their email
# authorization: admin or user that owns the project
@router.post("/share", status_code=status.HTTP_200_OK)
def share_project(
    request: schemas.ShareProject,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return userproject.share_exposed(
        current_user.email,
        current_user.role,
        request.beneficiary_email,
        request.project_id,
        db,
    )


# cancel sharing a project with a specific user by providing their email
# authorization: admin or user that owns the project
@router.post("/cancel_share", status_code=status.HTTP_200_OK)
def cancel_share_project(
    request: schemas.ShareProject,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return userproject.user_cancel_share(
        current_user.email,
        current_user.role,
        request.beneficiary_email,
        request.project_id,
        db,
    )


# check if the project is shared with the user
# authorization: any + login required
@router.post("/is_shared", status_code=status.HTTP_200_OK)
def check_if_project_is_shared_with_user(
    request: schemas.UserProject,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return userproject.check_shared(request.user_id, request.project_id, db)


# get the list of projects shared with the user
# authorization: any + login required
@router.get(
    "/shared_list",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ShowSharedProject],
)
def get_list_of_projects_shared_with_user(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return userproject.shared_projects_exposed(current_user.email, db)


# get the list of user with which the project is shared
# authorization: admin or user that owns the project
@router.get("/beneficiaries/{project_id}", status_code=status.HTTP_200_OK)
def get_list_of_beneficiaries_by_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return userproject.check_beneficiaries(
        project_id, current_user.email, current_user.role, db
    )


# get the list of projects shared with a user by id
# authorization: admin
@router.get("/admin/shared_list/{user_id}", status_code=status.HTTP_200_OK)
def get_list_of_projects_shared_with_user_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_admin),
):
    return userproject.shared_projects(user_id, db)


# get the project owner by project id
# authorization: any + login required
@router.get(
    "/get_owner/{project_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.ShowOwner,
)
def get_owner_name_by_project_id(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return userproject.get_owner(current_user.email, project_id, db)
