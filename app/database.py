from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

""" user_name = "user"
password = "2f2kir2y49xy6g"
host = "db"  
database_name = "fmdeploy_db"

DATABASE = 'mysql://%s:%s@%s/%s?charset=utf8' % (
    user_name,
    password,
    host,
    database_name,
)

engine = create_engine(
    DATABASE,
    encoding="utf-8",
    echo=True
) """

SQLALCHAMY_DATABASE_URL = 'mysql+mysqlconnector://root:1875mdfm@localhost:3306/fmdeploy_db'

engine = create_engine(SQLALCHAMY_DATABASE_URL) #, echo=true

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()