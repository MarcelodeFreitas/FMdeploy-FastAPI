from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Project(BaseModel):
    project_id: str
    title: str
    description: Optional[str] = None
    input_type: str
    output_type: str
    is_private: bool
    python_script_name: Optional[str] = None
    python_script_path: Optional[str] = None
    created_in: datetime 
    last_updated: Optional[datetime] = None
    class Config():
        orm_mode = True

class ShowProject(BaseModel):
    project_id: str
    name: str
    title: str
    description: Optional[str] = None
    input_type: str
    output_type: str
    is_private: bool
    created_in: datetime 
    last_updated: Optional[datetime] = None
    class Config():
        orm_mode = True
        
class ShowSharedProject(BaseModel):
    project_id: str
    title: str
    description: Optional[str] = None
    input_type: str
    output_type: str
    is_private: bool
    created_in: datetime 
    last_updated: Optional[datetime] = None

class CreateProject(BaseModel):
    user_id: int
    title: str
    description: Optional[str]
    input_type: str
    output_type: str
    is_private: bool
    class Config():
        orm_mode = True

class CreateProjectCurrent(BaseModel):
    title: str
    description: Optional[str]
    input_type: str
    output_type: str
    is_private: bool

class CreatedProject(BaseModel):
    project_id: str

class UpdateProject(BaseModel):
    project_id: str
    title:  Optional[str] = None
    description: Optional[str] = None
    input_type: Optional[str] = None
    output_type:  Optional[str] = None
    is_private:  Optional[bool] = None
    class Config():
        orm_mode = True

class RunProjectAdmin(BaseModel):
    user_id: int
    project_id: str
    input_file_id: str

    class Config():
        orm_mode = True

class RunProject(BaseModel):
    project_id: str
    input_file_id: str
    class Config():
        orm_mode = True

class User(BaseModel):
    name: str
    email: str

class ShowUser(BaseModel):
    """ user_id: str """
    name: str
    email: str
    class Config():
        orm_mode = True

class ShowUserAdmin(BaseModel):
    user_id: str 
    name: str
    email: str
    is_admin: bool
    class Config():
        orm_mode = True

class CreateUser(BaseModel):
    name: str
    email: str
    password: str
    class Config():
        orm_mode = True

class UpdateUser(BaseModel):
    new_name: Optional[str] = None
    new_email: Optional[str] = None
    new_password: Optional[str] = None
    class Config():
        orm_mode = True

class Owner(BaseModel):
    owner: bool
    class Config():
        orm_mode = True
        
class ShowOwner(BaseModel):
    name: str

class ModelFile(BaseModel):
    model_file_id: int
    fk_project_id: str
    name: Optional[str] = None
    path: Optional[str] = None
    class Config():
        orm_mode = True

class UserProject(BaseModel):
    user_id: int
    project_id: str
    class Config():
        orm_mode = True

class ShareProject(BaseModel):
    beneficiary_email: str
    project_id: str
    class Config():
        orm_mode = True

class AdminShareProject(BaseModel):
    user_id_sharer: int
    user_id_beneficiary: int
    project_id: str
    class Config():
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None