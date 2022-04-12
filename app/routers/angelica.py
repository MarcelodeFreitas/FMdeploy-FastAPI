from fastapi import APIRouter, File, UploadFile, status
from ..angelica_service import test
import os
import uuid
import shutil

router = APIRouter(
    prefix="/angelica",
    tags=['Services angelica'],
)


@router.post("/predict", status_code = status.HTTP_200_OK)
def predict(file: UploadFile = File(...)):
    
    id = uuid.uuid4()
    name_file= str(id)+".wav"

    with open(name_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    
    prev= test.prev_label(name_file)
    os.remove(name_file)
        
    return {"label": prev}
