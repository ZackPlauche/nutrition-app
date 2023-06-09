from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .db import engine

Session = scoped_session(sessionmaker(bind=engine))