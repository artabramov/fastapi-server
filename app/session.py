"""Provides Postgres database session object."""
# from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
# from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker
from app.dotenv import get_config



config = get_config()
sqlalchemy_uri = 'postgresql+asyncpg://%s:%s@%s:%s/%s' % (
    config.SQLALCHEMY_USERNAME, config.SQLALCHEMY_PASSWORD, config.SQLALCHEMY_HOST, config.SQLALCHEMY_PORT,
    config.SQLALCHEMY_DATABASE)

engine = create_async_engine(sqlalchemy_uri, echo=True, future=True)
Base = declarative_base()


def async_session_generator():
    return sessionmaker(
        engine, class_=AsyncSession
    )

async def get_session():
    """Return SQLAlchemy session object."""
    try:
        async_session = async_session_generator()
        async with async_session() as session:
            yield session
    finally:
        session.close()

# @asynccontextmanager
# async def get_session():
#     try:
#         async_session = async_session_generator()

#         async with async_session() as session:
#             yield session
#     except Exception as e:
#         await session.rollback()
#         raise e
#     finally:
#         await session.close()

# SessionLocal = sessionmaker(autocommit=config.SQLALCHEMY_AUTOCOMMIT, autoflush=config.SQLALCHEMY_AUTOFLUSH, bind=engine)

# Base = declarative_base()


# def get_session():
#     """Return SQLAlchemy session object."""
#     session = SessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()
