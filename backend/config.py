from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging

DATABASE_URL = 'postgresql://postgres:psqlpwd1234@localhost:5432/tazi'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logconf = logging.basicConfig(level=logging.DEBUG,
                              format='(%(threadName)-9s) %(message)s',)
