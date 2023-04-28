from fastapi import APIRouter, status, Depends
from .. import schemas, models, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import userproject, runhistory

router = APIRouter(prefix="/runhistory", tags=["Run History"])


# get run history
@router.get(
    "", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowRunHistory]
)
def get_run_history(
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return runhistory.get_current(get_current_user, db)


""" # update run history entry
@router.put(
    "", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.ShowRunHistory
)
def update_run_history_entry(
    request: schemas.UpdateProject,
    db: Session = Depends(get_db),
    get_current_user: schemas.User = Depends(oauth2.get_current_user),
):
    return runhistory.update_by_id(get_current_user, db, request) """
