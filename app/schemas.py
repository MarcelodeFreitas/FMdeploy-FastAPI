from pydantic import BaseModel, constr
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

    class Config:
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

    class Config:
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

    class Config:
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
    title: Optional[str] = None
    description: Optional[str] = None
    input_type: Optional[str] = None
    output_type: Optional[str] = None
    is_private: Optional[bool] = None

    class Config:
        orm_mode = True


class RunProjectAdmin(BaseModel):
    user_id: int
    project_id: str
    input_file_id: str

    class Config:
        orm_mode = True


class RunProject(BaseModel):
    project_id: str
    input_file_id: str

    class Config:
        orm_mode = True


class User(BaseModel):
    name: str
    email: str


class ShowUser(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True


class ShowUserAdmin(BaseModel):
    user_id: str
    name: str
    email: str
    role: str

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class CreateUserAdmin(BaseModel):
    name: str
    email: str
    password: str
    role: constr(regex="^(admin|guest|user)$")

    class Config:
        orm_mode = True


class UpdateUser(BaseModel):
    new_name: Optional[str] = None
    new_email: Optional[str] = None
    new_password: Optional[str] = None

    class Config:
        orm_mode = True


class UpdateUserAdmin(BaseModel):
    user_email: str
    new_name: Optional[str] = None
    new_email: Optional[str] = None
    new_password: Optional[str] = None
    new_role: Optional[constr(regex="^(admin|guest|user)?$")] = None

    class Config:
        orm_mode = True


class Owner(BaseModel):
    owner: bool

    class Config:
        orm_mode = True


class ShowOwner(BaseModel):
    name: str
    email: str


class ModelFile(BaseModel):
    model_file_id: int
    fk_project_id: str
    name: Optional[str] = None
    path: Optional[str] = None

    class Config:
        orm_mode = True


class UserProject(BaseModel):
    user_id: int
    project_id: str

    class Config:
        orm_mode = True


class ShareProject(BaseModel):
    beneficiary_email: str
    project_id: str

    class Config:
        orm_mode = True


class AdminShareProject(BaseModel):
    user_id_sharer: int
    user_id_beneficiary: int
    project_id: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str
    role: str


class ShowRunHistory(BaseModel):
    run_history_id: int
    project_id: str
    title: str
    description: Optional[str] = None
    email: str
    name: str
    flagged: bool
    flag_description: Optional[str] = None
    timestamp: datetime
    fk_input_file_id: str
    input_file_name: str
    input_file_path: str
    fk_output_file_id: Optional[str] = None
    output_file_name: Optional[str] = None
    output_file_path: Optional[str] = None


class CreateRunHistory(BaseModel):
    fk_user_id: int
    fk_project_id: str
    fk_input_file_id: str
    fk_output_file_id: Optional[str] = None
    flagged: bool
    flag_description: Optional[str] = None

    class Config:
        orm_mode = True


class UpdateRunHistory(BaseModel):
    run_history_id: int
    flagged: Optional[bool] = False
    flag_description: Optional[str] = None
    fk_output_file_id: Optional[str] = None
    output_file_name: Optional[str] = None
    output_file_path: Optional[str] = None

    class Config:
        orm_mode = True


class RunHistoryFlag(BaseModel):
    run_history_id: int
    flagged: bool
    flag_description: Optional[str] = None

    class Config:
        orm_mode = True


class RunHistoryFlagOutput(BaseModel):
    output_file_id: str
    flagged: bool
    flag_description: Optional[str] = None

    class Config:
        orm_mode = True


class RunHistoryFlagInput(BaseModel):
    input_file_id: str
    flagged: bool
    flag_description: Optional[str] = None

    class Config:
        orm_mode = True
