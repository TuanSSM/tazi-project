from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = 'postgresql://postgres:' + insert_secret_pwd '@localhost:5432/tazi'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autflush=False, bind=engine)
Base = declarative_base()
