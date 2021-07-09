from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AI(BaseModel):
    ai_id: int
    title: str
    description: Optional[str] = None
    output_type: str
    is_private: bool
    python_script_name: Optional[str] = None
    python_script_path: Optional[str] = None
    timestamp: datetime 
    last_updated: Optional[datetime] = None

    class Config():
        orm_mode = True

class CreateAI(BaseModel):
    title: str
    description: Optional[str]
    output_type: str
    is_private: bool
    timestamp: datetime

    class Config():
        orm_mode = True

class UpdateAI(BaseModel):
    title: str
    description: Optional[str] = None
    output_type: str
    is_private: bool
    last_updated: datetime

    class Config():
        orm_mode = True

class ShowAI(BaseModel):
    ai_id: int
    title: str
    description: Optional[str] = None
    output_type: str
    is_private: bool
    python_script_name: Optional[str] = None
    python_script_path: Optional[str] = None
    timestamp: datetime 
    last_updated: Optional[str] = None

    class Config():
        orm_mode = True

# class UpdatePythonScript(BaseModel):
#     name: str
#     path: str

#     class Config():
#         orm_mode = True
