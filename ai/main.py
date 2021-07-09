from fastapi import FastAPI, Depends, File, UploadFile, status, Response, HTTPException
from fastapi.responses import HTMLResponse
from . import schemas, models
from .database import engine
from sqlalchemy.orm import Session
from .database import get_db
from typing import List
import shutil
import os
from datetime import datetime
import json


app = FastAPI()

#when we run the server migrate all the models to the database
#if the table exists nothing happens
#if not, the table is created
models.Base.metadata.create_all(engine)

#save documentation
@app.on_event("startup")
def save_openapi_json():
    openapi_data = app.openapi()
    # Change "openapi.json" to desired filename
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)

#create user
@app.post('/user', status_code = status.HTTP_201_CREATED)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    new_user = models.User(name=request.name, email=request.email, password=request.password)
    try: 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Email is already registered!")
    return new_user

#get all users
@app.get('/user', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowUser])
def get_all_users(db: Session = Depends(get_db)):
    user_list = db.query(models.User).all()
    return user_list

#get ai model by id
@app.get('/user/{user_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowUser)
def get_user_by_id(user_id, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id number {user_id} was not found!")
    return user

#delete user by id
@app.delete('/user/{user_id}', status_code = status.HTTP_200_OK)
def delete_user(user_id, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found!")
    user.delete(synchronize_session=False)
    db.commit()
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"User id {user_id} was successfully deleted.")

@app.put('/user/{user_id}', status_code = status.HTTP_202_ACCEPTED)
def update_user_by_id(user_id, request: schemas.UpdateUser, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found!")
    try:
        user.update(request.dict())
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Email is already registered!")
    return user.first()

#create ai model
@app.post('/ai', status_code = status.HTTP_201_CREATED)
def create_ai(request: schemas.CreateAI, db: Session = Depends(get_db)):
    new_ai = models.AI(title=request.title, description=request.description, output_type=request.output_type,is_private=request.is_private, timestamp=request.timestamp)
    db.add(new_ai)
    db.commit()
    db.refresh(new_ai)
    return new_ai

#get all public ai models
@app.get('/ai', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowAI])
def get_all_ai(db: Session = Depends(get_db)):
    ai_list = db.query(models.AI).all()
    return ai_list

#get all ai models
@app.get('/privacy', status_code = status.HTTP_200_OK, response_model=List[schemas.AI])
def get_all_public_ai(db: Session = Depends(get_db)):
    ai_list =  db.query(models.AI).where(models.AI.is_private.is_(False)).all()
    for i in ai_list:
        if i.is_private == False:
            print(i.is_private)
            print(type(i.is_private))
    return ai_list

#get ai model by id
@app.get('/ai/{ai_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowAI)
def get_ai_by_id(ai_id, response: Response, db: Session = Depends(get_db)):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id).first()
    if not ai:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"AI model with id number {ai_id} was not found!")
    return ai

@app.delete('/ai/{ai_id}', status_code = status.HTTP_200_OK)
def delete_ai(ai_id, db: Session = Depends(get_db)):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
    if not ai.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
    ai.delete(synchronize_session=False)
    db.commit()
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"The AI model id {ai_id} was successfully deleted.")

@app.put('/ai/{ai_id}', status_code = status.HTTP_202_ACCEPTED)
def update_ai_by_id(ai_id, request: schemas.UpdateAI, db: Session = Depends(get_db)):
    ai = db.query(models.AI).filter(models.AI.ai_id == ai_id)
    if not ai.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI model with id {ai_id} not found!")
    ai.update(request.dict())
    db.commit()
    return ai.first()

#upload python script
@app.post("/ai/files/pythonscript")
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


#upload model files h5
@app.post("/ai/files/modelfiles")
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

    return HTTPException(status_code=status.HTTP_200_OK, detail=f"The file named {file_name} was successfully submited to model id number {ai_id}.")



# #requesting and saving files
# @app.post("/files/")
# async def create_files(files: List[bytes] = File(...)):
#     return {"file_sizes": [len(file) for file in files]}

# @app.post("/uploadfiles/")
# async def create_upload_files(files: List[UploadFile] = File(...)):
#     for file in files:
#         with open(f"{file.filename}", "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)  
#     return {"filenames": [file.file for file in files]}

# @app.post("/uploadfile")
# async def create_upload_files(file: UploadFile = File(...)):
#     with open("test.mp4", "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)  
#     return {"filenames": file.filename}


@app.get("/")
async def main():
    content = """
<body>
<form action="/ai/files/pythonscript" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<a href="/docs">docs</a>
</body>
    """
    return HTMLResponse(content=content)