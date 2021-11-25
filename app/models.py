from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from .database import Base
from sqlalchemy.orm import relationship

#Database table and relationship creation
#SQLAlchemy calls the shemas by the name model

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, index=True)
    userailist = relationship("UserAIList")
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False, nullable=True)
    
class UserAIList(Base):
    __tablename__ = 'userailist'
    user_ai_list_id = Column(Integer, primary_key=True, index=True)
    fk_user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    fk_ai_id = Column(String, ForeignKey('ai.ai_id'), nullable=False)
    owner =  Column(Boolean, default=False, nullable=False)
    
class AI(Base):
    __tablename__ = 'ai'
    ai_id = Column(String, primary_key=True, index=True)
    userailist = relationship("UserAIList")
    ai_files = relationship("ModelFile")
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    input_type = Column(String, nullable=False)
    output_type = Column(String, nullable=False)
    python_script_name = Column(String, nullable=True)
    python_script_path = Column(String, nullable=True)
    is_private = Column(Boolean, default=True, nullable=False)
    created_in = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=True)
    
class ModelFile(Base):
    __tablename__ = 'modelfile'
    model_file_id = Column(Integer, primary_key=True, index=True)
    fk_ai_id = Column(String, ForeignKey('ai.ai_id'))
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)

class InputFile(Base):
    __tablename__ = 'inputfile'
    input_file_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)