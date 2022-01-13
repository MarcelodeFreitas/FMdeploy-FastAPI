from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

""" SQLALCHAMY_DATABASE_URL = 'sqlite:///./database.db' """
""" SQLALCHAMY_DATABASE_URL = 'sqlite:///./database.db' """
""" SQLALCHAMY_DATABASE_URL = 'postgresql://postgres:2f2kir2y49xy6g@localhost/fmdeploy_db' """
SQLALCHAMY_DATABASE_URL = 'mysql+mysqlconnector://root:1875mdfm@localhost:3306/fmdeploy_db'

engine = create_engine(SQLALCHAMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False,)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()