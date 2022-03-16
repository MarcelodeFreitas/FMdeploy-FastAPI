from fastapi import APIRouter, status, Depends
from .. import schemas, oauth2
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from ..repository import project

router = APIRouter(
    prefix="/project",
    tags=['Projects']
)

#get all projects
@router.get('/admin', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowProject])
def get_all_projects(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.get_all_exposed(get_current_user, db)

#update project data
@router.put('', status_code = status.HTTP_202_ACCEPTED)
def update_project(request: schemas.UpdateProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.update_by_id_exposed(get_current_user, request.project_id, request.title, request.description, request.input_type, request.output_type, request.is_private, db)

#create project
@router.post('/admin', status_code = status.HTTP_201_CREATED, response_model=schemas.CreatedProject)
def create_project_by_admin(request: schemas.CreateProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.create_by_admin(get_current_user, request, db)

#create project with current user
@router.post('', status_code = status.HTTP_201_CREATED, response_model=schemas.CreatedProject)
def create_project(request: schemas.CreateProjectCurrent, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.create_by_current(request, get_current_user, db)

#get all public projects
@router.get('/public', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowProject])
def get_all_public_projects(db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.get_all_public(db)

#get public projects by id
@router.get('/public/{project_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowProject)
def get_public_project_by_id(project_id: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.get_public_by_id_exposed(project_id, db)

#get public project by title
@router.get('/public/title/{title}', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowProject])
def get_public_project_by_title(title: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.get_public_by_title_exposed(title, db)

#get project by id
@router.get('/{project_id}', status_code = status.HTTP_200_OK, response_model=schemas.ShowProject)
def get_project_by_id(project_id: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.get_by_id_exposed(get_current_user, project_id, db)

#get project by title
@router.get('/admin/title/{title}', status_code = status.HTTP_200_OK, response_model=List[schemas.ShowProject])
def get_project_by_title(title: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.get_by_title_exposed(get_current_user, title, db)

#delete project from database tables and filesystem
@router.delete('/{project_id}', status_code = status.HTTP_200_OK)
def delete_project(project_id: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.delete(get_current_user, project_id, db)

#delete project from database tables and filesystem
@router.delete('/admin/{project_id}', status_code = status.HTTP_200_OK)
def delete_project_admin(project_id: str, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return project.delete_admin(get_current_user, project_id, db)

#run an project with current user
@router.post('/run', status_code = status.HTTP_202_ACCEPTED)
async def run_project(request: schemas.RunProject, db: Session = Depends(get_db), get_current_user: schemas.User = Depends(oauth2.get_current_user)):
    return await project.run(get_current_user, request.project_id, request.input_file_id, db)