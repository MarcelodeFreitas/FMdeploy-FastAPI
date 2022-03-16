from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import event, DDL

#Database table and relationship creation
#SQLAlchemy calls the shemas by the name model

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), nullable=False)
    email = Column(String(length=255), unique=True, nullable=False)
    password = Column(String(length=255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=True)
    userproject = relationship("UserProject", backref="User", passive_deletes=True)
    occurrence = relationship("Occurrence", backref="User", passive_deletes=True)
    
# add one admin the database after the table User is created
event.listen(User.__table__, 'after_create',
            DDL(" INSERT INTO user (name, email, password, is_admin) VALUES ('admin', 'fmdeploy@gmail.com', '$2b$12$cm7LbkGUMSzbWe9fAdCXJO/lzivm49UHi4aEGR21bpbQ5aX6a4hdS', TRUE) "))
    
class UserProject(Base):
    __tablename__ = 'userproject'
    user_project_list_id = Column(Integer, primary_key=True, index=True)
    fk_user_id = Column(Integer, ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    fk_project_id = Column(String(length=255), ForeignKey('project.project_id', ondelete='CASCADE'), nullable=False)
    owner =  Column(Boolean, default=False, nullable=False)
    
class Project(Base):
    __tablename__ = 'project'
    project_id = Column(String(length=255), primary_key=True, index=True)
    title = Column(String(length=255), nullable=False)
    description = Column(String(length=255), nullable=False)
    input_type = Column(String(length=255), nullable=False)
    output_type = Column(String(length=255), nullable=False)
    python_script_name = Column(String(length=255), nullable=True)
    python_script_path = Column(String(length=255), nullable=True)
    is_private = Column(Boolean, default=True, nullable=False)
    created_in = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=True)
    modelfile = relationship("ModelFile", backref="Project", passive_deletes=True)
    occurrence = relationship("Occurrence", backref="Project", passive_deletes=True)
    
class ModelFile(Base):
    __tablename__ = 'modelfile'
    model_file_id = Column(Integer, primary_key=True, index=True)
    fk_project_id = Column(String(length=255), ForeignKey('project.project_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(length=255), nullable=False)
    path = Column(String(length=255), nullable=False)

class InputFile(Base):
    __tablename__ = 'inputfile'
    input_file_id = Column(String(length=255), primary_key=True, index=True)
    name = Column(String(length=255), nullable=False)
    path = Column(String(length=255), nullable=False)
    occurrence = relationship("Occurrence", backref="InputFile", passive_deletes=True)
    
class OutputFile(Base):
    __tablename__ = 'outputfile'
    output_file_id = Column(String(length=255), primary_key=True, index=True)
    name = Column(String(length=255), nullable=False)
    path = Column(String(length=255), nullable=False)
    occurrence = relationship("Occurrence", backref="OutputFile", passive_deletes=True)
        
class Occurrence(Base):
    __tablename__ = 'occurrence'
    ocurrence_id = Column(String(length=255), primary_key=True, index=True)
    flagged = Column(Boolean, default=False, nullable=True)
    flag_description = Column(String(length=255), nullable=True)
    fk_user_id = Column(Integer, ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    fk_project_id = Column(String(length=255), ForeignKey('project.project_id', ondelete='CASCADE'), nullable=False)
    fk_input_file_id = Column(String(length=255), ForeignKey('inputfile.input_file_id', ondelete='CASCADE'), nullable=False)
    fk_output_file_id = Column(String(length=255), ForeignKey('outputfile.output_file_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False)