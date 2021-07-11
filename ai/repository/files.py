from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
import os

def check_model_files(ai_id: str, db):
    modelfiles = db.query(models.ModelFile).where(models.ModelFile.fk_ai_id == ai_id).all()
    if not modelfiles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} has no model files!")
    for modelfile in modelfiles:   
        if modelfile.path == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI model with id number {ai_id} does not have model files!")
        if os.path.isfile(modelfile.path) == False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI model with id number: {ai_id}, path: {modelfile.path}, does not exist in the filesystem !")
    return True