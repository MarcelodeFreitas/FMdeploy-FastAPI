from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from .database import Base
from sqlalchemy.orm import relationship

#Database table and relationship creation
#SQLAlchemy calls the shemas by the name model

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    model_list = relationship("Association")

class Model(Base):
    __tablename__ = 'model'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    output_type = Column(String, nullable=False)
    python_script_path = Column(String, nullable=False)
    python_script_name = Column(String, nullable=False)
    is_private = Column(Boolean, default=True, nullable=False)
    created_in = Column(DateTime, nullable=False)
    model_files = relationship("ModelFile", back_populates="id")

class ModelUserList(Base):
    __tablename__ = 'modeluserlist'
    fk_model_id = Column(Integer, ForeignKey('model.id'), primary_key=True)
    fk_user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

class ModelFile(Base):
    __tablename__ = 'modelfile'
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    models = relationship("Model", back_populates="id")