from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from .database import Base
from sqlalchemy.orm import relationship

#Database table and relationship creation
#SQLAlchemy calls the shemas by the name model

class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    creator = relationship("User", back_populates="blogs")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    blogs = relationship('Blog', back_populates="creator")
    model_list = relationship("Model", back_populates="id")

class Model(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    python_script_path = Column(String, nullable=False)
    input_type = Column(String, nullable=False)
    output_type = Column(String, nullable=False)
    is_private = Column(Boolean, default=True, nullable=False)
    created_in = Column(DateTime, nullable=False)
    paths = relationship("Path", back_populates="id")
    user_list = relationship("User", back_populates="id")

class Path(Base):
    __tablename__ = 'path'

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False)
    description = Column(String, nullable=True)
    models = relationship("Model", back_populates="id")





