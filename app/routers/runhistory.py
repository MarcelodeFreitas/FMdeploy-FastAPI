from fastapi import APIRouter, status, Depends
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import userproject, runhistory

router = APIRouter(prefix="/runhistory", tags=["Run History"])


# get run history
# authorization: any
@router.get(
    "", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowRunHistory]
)
def get_run_history(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return runhistory.get_current(current_user.email, db)


# get flagged outputs for project
# authorization: admin or user that owns the project
@router.get(
    "/flagged/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ShowRunHistory],
)
def get_flagged_outputs(
    project_id,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.this_user_or_admin),
):
    return runhistory.get_project_flagged_outputs(
        db, current_user.email, current_user.role, project_id
    )


# update flag and flag description in run history table entry
# athorization: any + login required
@router.put("/flag", status_code=status.HTTP_202_ACCEPTED)
def flag_run_history_entry(
    request: schemas.RunHistoryFlagInput,
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return runhistory.flag_by_input_file_id(get_current_user, db, request)
