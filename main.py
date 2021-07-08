from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI()

class AI(BaseModel):
    id: int
    title: str
    description: Optional[str]
    python_script_name: str
    python_script_path: str
    output_type: str
    is_private: bool
    created_in: datetime


@app.get('/')
def index():
    return 'hey'

@app.get('/ai/{id}')
def show(id: int):
    return {'data': id}

@app.post('/ai')
def create_ai(ai: AI):
    return ai
    return {'data': "Blog is created"}

