"""Provides Postgres database session object."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.dotenv import get_config


config = get_config()
engine = create_engine(config.SQLALCHEMY_URI)
SessionLocal = sessionmaker(autocommit=config.SQLALCHEMY_AUTOCOMMIT, autoflush=config.SQLALCHEMY_AUTOFLUSH, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    """Return SQLAlchemy session object."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
