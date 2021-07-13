from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AI(BaseModel):
    ai_id: str
    title: str
    description: Optional[str] = None
    output_type: str
    is_private: bool
    python_script_name: Optional[str] = None
    python_script_path: Optional[str] = None
    created_in: datetime 
    last_updated: Optional[datetime] = None

    class Config():
        orm_mode = True

class ShowAI(BaseModel):
    ai_id: str
    title: str
    description: Optional[str] = None
    output_type: str
    is_private: bool
    created_in: datetime 
    last_updated: Optional[datetime] = None

    class Config():
        orm_mode = True

class CreateAI(BaseModel):
    user_id: int
    title: str
    description: Optional[str]
    output_type: str
    is_private: bool
    created_in: datetime

    class Config():
        orm_mode = True

class CreatedAI(BaseModel):
    ai_id: str


class UpdateAI(BaseModel):
    title: str
    description: Optional[str] = None
    output_type: str
    is_private: bool
    last_updated: datetime

    class Config():
        orm_mode = True

class User(BaseModel):
    user_id: str
    name: str
    email: str
    password: str

    class Config():
        orm_mode = True

class ShowUser(BaseModel):
    user_id: str
    name: str
    email: str

    class Config():
        orm_mode = True

class CreateUser(BaseModel):
    name: str
    email: str
    password: str

    class Config():
        orm_mode = True

class UpdateUser(BaseModel):
    name: str
    email: str

    class Config():
        orm_mode = True

class RunAI(BaseModel):
    user_id: int
    ai_id: str
    input_file_id: str

    class Config():
        orm_mode = True

class UserAIList(BaseModel):
    user_ai_list_id: int
    fk_user_id: int
    fk_ai_id: str
    owner: bool
    beneficiary: bool
    
    class Config():
        orm_mode = True

class Owner(BaseModel):
    owner: bool
    
    class Config():
        orm_mode = True

class ModelFile(BaseModel):
    model_file_id: int
    fk_ai_id: str
    name: Optional[str] = None
    path: Optional[str] = None

    class Config():
        orm_mode = True

class UserAI(BaseModel):
    user_id: int
    ai_id: str

    class Config():
        orm_mode = True

class ShareAI(BaseModel):
    user_id_sharer: int
    user_id_beneficiary: int
    ai_id: str

    class Config():
        orm_mode = True


