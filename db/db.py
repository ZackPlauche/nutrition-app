from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Date, Float
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, DeclarativeMeta, scoped_session
from sqlalchemy.exc import IntegrityError

from .models import Base


engine = create_engine('sqlite:///db.sqlite3')

Session = scoped_session(sessionmaker(bind=engine))


