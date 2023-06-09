from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeMeta, declarative_base
from sqlalchemy.exc import IntegrityError

from db.session import Session

Base: DeclarativeMeta = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
    
    def save(self):
        """Save the object to the database."""
        session = Session()
        try:
            session.add(self)
            session.commit()
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                print(f'{self.__class__.__name__} with that name already exists')
                session.rollback()
            else:
                raise e
        return self
    
    def is_detached(self):
        """Check if the object is detached from a session."""
        session = Session.object_session(self)
        return session is None or session.is_modified(self)

    def delete(self, commit=True):
        """Delete the object from the database."""
        session = Session()
        session.delete(self)
        session.commit()


    @classmethod
    def _validate_kwargs(cls, **kwargs):
        """Validate that key word arguments are valid column names."""
        for key in kwargs.keys():
            if not hasattr(cls, key):
                raise ValueError(f'{cls.__class__.__name__} has no attribute {key}')

    @classmethod
    def get(cls, **kwargs):
        """Get an object of this type by keyword arguments."""
        cls._validate_kwargs(**kwargs)
        session = Session()
        obj = session.query(cls).filter_by(**kwargs).first()
        return obj
    
    @classmethod
    def get_all(cls):
        """Get all objects of this type."""
        session = Session()
        objs = session.query(cls).all()
        return objs
    
    @classmethod
    def query(cls):
        """Get a query object for this type."""
        session = Session()
        return session.query(cls)

