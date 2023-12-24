"""Provides session object."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine("postgresql+psycopg2://memo:he7w2rLY4Y8pFk2u@localhost:5432/memo")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    """Return SQLAlchemy session object."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
