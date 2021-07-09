from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from .database import Base
from sqlalchemy.orm import relationship

#Database table and relationship creation
#SQLAlchemy calls the shemas by the name model

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    userailist = relationship("UserAIList")
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    
class UserAIList(Base):
    __tablename__ = 'userailist'
    id = Column(Integer, primary_key=True, index=True)
    fk_user_id = Column(Integer, ForeignKey('user.id'))
    fk_model_id = Column(Integer, ForeignKey('ai.id'))
    owner =  Column(Boolean, default=False, nullable=False)
    
class AI(Base):
    __tablename__ = 'ai'
    id = Column(Integer, primary_key=True, index=True)
    userailist = relationship("UserAIList")
    ai_files = relationship("ModelFile")
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    output_type = Column(String, nullable=False)
    python_script_name = Column(String, nullable=False)
    python_script_path = Column(String, nullable=False)
    is_private = Column(Boolean, default=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
class ModelFile(Base):
    __tablename__ = 'modelfile'
    id = Column(Integer, primary_key=True, index=True)
    fk_model_id = Column(Integer, ForeignKey('ai.id'))
    path = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)