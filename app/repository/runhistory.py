from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .. import schemas, models
from datetime import datetime
from typing import Optional
import logging

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

