from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from .. import schemas, models
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import ai, user, files
import shutil
import os
import importlib
import sys

router = APIRouter(
    prefix="/ai",
    tags=['AI models']
)

#AI

@router.get("/test", status_code = status.HTTP_200_OK)
def test(db: Session = Depends(get_db)):
    path = "./modelfiles/69b743c6b88d415cb56fa917373a55fd/Generate_OB_masks_module.py"
    name = "Generate_OB_masks_module"
    file_exists = os.path.isfile(path)
    directory = os.path.isdir("./modelfiles/69b743c6b88d415cb56fa917373a55fd")
    sys.path.append('./modelfiles/69b743c6b88d415cb56fa917373a55fd')
    script = importlib.import_module(name)
    return {"file_exists": name[0:-3], "directory": directory, "hey": script.hello()}

#run a model by id
@router.post('/run', status_code = status.HTTP_202_ACCEPTED)
async def run_ai(request: schemas.RunAI, db: Session = Depends(get_db)):
    return await ai.run_ai(request.user_id, request.ai_id, request.input_file_id, db)

#create ai model
@router.post('/', status_code = status.HTTP_201_CREATED, response_model=schemas.CreatedAI)
def create_ai(request: schemas.CreateAI, db: Session = Depends(get_db)):
    return ai.create_ai(request, db)

#get all ai models
@router.get('/', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_all_ai(db: Session = Depends(get_db)):
    return ai.get_all(db)

#get all public ai models
@router.get('/public', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_all_public_ai(db: Session = Depends(get_db)):
    ai_list =  db.query(models.AI).where(models.AI.is_private.is_(False)).all()
    return ai_list

#get public ai models by id
@router.get('/public/{ai_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowAI)
def get_all_public_ai_by_id(ai_id, db: Session = Depends(get_db)):
    ai =  db.query(models.AI).where(models.AI.is_private.is_(False)).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found in Public AIs!")
    return ai

#get oublic ai model by title
@router.get('/public/title/{title}', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_public_ai_by_title(title, db: Session = Depends(get_db)):
    ai = db.query(models.AI).where(models.AI.is_private.is_(False)).filter(models.AI.title.like(f"%{title}%")).all()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with title: {title} was not found!")
    return ai

#get ai model by id
@router.get('/{ai_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowAI)
def get_ai_by_id(ai_id, db: Session = Depends(get_db)):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found!")
    return ai

#get ai model by title
@router.get('/title/{title}', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_ai_by_title(title, db: Session = Depends(get_db)):
    ai = db.query(models.AI).filter(models.AI.title.like(f"%{title}%")).all()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with title: {title} was not found!")
    return ai

@router.delete('/{ai_id}', status_code = status.HTTP_200_OK)
def delete_ai(ai_id, db: Session = Depends(get_db)):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
    if not ai.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
    ai.delete(synchronize_session=False)
    db.commit()
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"The AI model id {ai_id} was successfully deleted.")

@router.put('/{ai_id}', status_code = status.HTTP_202_ACCEPTED, response_model=schemas.ShowAI)
def update_ai_by_id(ai_id, request: schemas.UpdateAI, db: Session = Depends(get_db)):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
    if not ai.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
    ai.update(request.dict())
    db.commit()
    return ai.first()

#upload input file
@router.post("/files/inputfile", status_code = status.HTTP_200_OK)
def create_input_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return files.create_input_file(db, file)

#upload python script
@router.post("/files/pythonscript")
async def create_script_file(model_id, file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    file_name = file.filename
    file_path = "./modelfiles/" + model_id + "/" + file_name

    ai = db.query(models.AI).filter(models.AI.ai_id == model_id)
    #check if provided model_id is valid
    if not ai.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {model_id} not found!")
    #check if model already has python script
    if ai.first().python_script_path != None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model id {model_id} already has a python script!")
    #try to update ai data fields related to python script
    try:
        ai.update({"python_script_name": file_name, "python_script_path": file_path })
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model id {model_id} database update error!")
    #try to write python script top filesystem
    try:
        os.makedirs("./modelfiles/" + model_id, exist_ok=True)
        with open(f"{file_path}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)  
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File named {file_name} filesystem write error!")

    return HTTPException(status_code=status.HTTP_200_OK, detail=f"The file named {file_name} was successfully submited to model id number {model_id}.")

#upload model files 
@router.post("/files/modelfiles")
async def create_model_file(ai_id, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    for file in files:
        file_name = file.filename
        file_path = "./modelfiles/" + ai_id + "/" + file_name

        ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
        #check if provided model_id is valid
        if not ai.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
        #create a new entry in the table model file
        try:
            new_modelfile = models.ModelFile(fk_ai_id=ai_id, name=file_name, path=file_path)
            db.add(new_modelfile)
            db.commit()
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model id {ai_id} database commit error!")
        #try to write python script top filesystem
        try:
            os.makedirs("./modelfiles/" + ai_id, exist_ok=True)
            with open(f"{file_path}", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)  
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File named {file_name} filesystem write error!")

    return HTTPException(status_code=status.HTTP_200_OK, detail=f"Files successfully submited to model id number {ai_id}.")

#get model files name and path stored for a specific ai model
@router.post("/files/check_model_files/{ai_id}", status_code = status.HTTP_200_OK)
def check_model_files_by_id(ai_id, db: Session = Depends(get_db)):
    return files.check_model_files(ai_id, db)

#get input file name and path stored by id
@router.post("/files/check_input_file/{input_file_id}", status_code = status.HTTP_200_OK)
def check_input_file_by_id(input_file_id, db: Session = Depends(get_db)):
    return files.check_input_file(input_file_id, db)

#get python file by id
@router.post("/files/check_python_file/{ai_id}", status_code = status.HTTP_200_OK)
def check_python_file_by_id(ai_id, db: Session = Depends(get_db)):
    return ai.check_python_files(ai_id, db)