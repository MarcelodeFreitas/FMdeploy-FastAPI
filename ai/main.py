from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.responses import HTMLResponse
from . import schemas, models
from .database import engine
from sqlalchemy.orm import Session
from .database import get_db
from typing import List
import shutil


app = FastAPI()

#when we run the server migrate all the models to the database
#if the table exists nothing happens
#if not, the table is created
models.Base.metadata.create_all(engine)

@app.post('/ai')
def create(request: schemas.AI, db: Session = Depends(get_db)):
    new_ai = models.AI(title=request.title, description=request.description, output_type=request.output_type,  python_script_path=request.python_script_path,python_script_name=request.python_script_name,is_private=request.is_private)
    db.add(new_ai)
    db.commit()
    db.refresh(new_ai)

@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}

@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        with open(f"{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)  
    return {"filenames": [file.file for file in files]}

@app.post("/uploadfile")
async def create_upload_files(file: UploadFile = File(...)):
    with open("test.mp4", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)  
    return {"filenames": file.filename}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)