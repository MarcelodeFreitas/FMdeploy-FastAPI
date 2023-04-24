from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .. import schemas, models
from . import user
from datetime import datetime
from typing import Optional
import logging

#get run hitory for current user
def get_current(user_email: str, db: Session):
    #get the user_id from user_email
    user_id = user.get_by_email(user_email, db).user_id
    #list entries where user_id is a fk_user_id in the run history table
    run_history = db.query(models.RunHistory, models.User, models.Project, models.InputFile, models.OutputFile ).where(models.RunHistory.fk_user_id == user_id).outerjoin(models.User).outerjoin(models.Project).outerjoin(models.InputFile).outerjoin(models.OutputFile).with_entities(models.RunHistory.flagged, models.RunHistory.flag_description, models.RunHistory.timestamp, models.RunHistory.fk_input_file_id, models.RunHistory.fk_output_file_id, models.User.email, models.User.name, models.Project.project_id, models.Project.title, models.Project.description, models.InputFile.name.label('input_file_name'), models.InputFile.path.label('input_file_path'), models.OutputFile.name.label('output_file_name'), models.OutputFile.path.label('output_file_path')).all()
    if not run_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Run History table is empty!")
    return run_history
#get all run history entries for current user

#create an entry in the run history table
def create_entry(db: Session, fk_user_id: int, fk_project_id: str, fk_input_file_id: str, fk_output_file_id: Optional[str] = None, flagged: bool = False, flag_description: Optional[str] = None):
    new = models.RunHistory(fk_user_id = fk_user_id, fk_project_id = fk_project_id, fk_input_file_id = fk_input_file_id, fk_output_file_id = fk_output_file_id, flagged = flagged, flag_description = flag_description, timestamp = datetime.now())
    try:
        db.add(new)
        db.commit()
        db.refresh(new)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"Project with id number {fk_project_id} error creating Run History table entry!")

#update an entry in the run history table
#used to update outputfile


#delete an entry in the run history table

