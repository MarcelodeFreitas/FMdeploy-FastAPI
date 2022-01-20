from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import event, DDL

#Database table and relationship creation
#SQLAlchemy calls the shemas by the name model

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, index=True)
    userailist = relationship("UserAIList")
    name = Column(String(length=255), nullable=False)
    email = Column(String(length=255), unique=True, nullable=False)
    password = Column(String(length=255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=True)
    
# add one admin the database
event.listen(User.__table__, 'after_create',
            DDL(" INSERT INTO user (name, email, password, is_admin) VALUES ('admin', 'fmdeploy@gmail.com', '$2b$12$cm7LbkGUMSzbWe9fAdCXJO/lzivm49UHi4aEGR21bpbQ5aX6a4hdS', TRUE) "))
    
class UserAIList(Base):
    __tablename__ = 'userailist'
    user_ai_list_id = Column(Integer, primary_key=True, index=True)
    fk_user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    fk_ai_id = Column(String(length=255), ForeignKey('ai.ai_id'), nullable=False)
    owner =  Column(Boolean, default=False, nullable=False)
    
class AI(Base):
    __tablename__ = 'ai'
    ai_id = Column(String(length=255), primary_key=True, index=True)
    userailist = relationship("UserAIList")
    ai_files = relationship("ModelFile")
    author = Column(String(length=255), nullable=False)
    title = Column(String(length=255), nullable=False)
    description = Column(String(length=255), nullable=False)
    input_type = Column(String(length=255), nullable=False)
    output_type = Column(String(length=255), nullable=False)
    python_script_name = Column(String(length=255), nullable=True)
    python_script_path = Column(String(length=255), nullable=True)
    is_private = Column(Boolean, default=True, nullable=False)
    created_in = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=True)
    
class ModelFile(Base):
    __tablename__ = 'modelfile'
    model_file_id = Column(Integer, primary_key=True, index=True)
    fk_ai_id = Column(String(length=255), ForeignKey('ai.ai_id'))
    name = Column(String(length=255), nullable=False)
    path = Column(String(length=255), nullable=False)

class InputFile(Base):
    __tablename__ = 'inputfile'
    input_file_id = Column(String(length=255), primary_key=True, index=True)
    name = Column(String(length=255), nullable=False)
    path = Column(String(length=255), nullable=False)