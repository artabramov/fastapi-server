from fastapi import FastAPI, Depends
from app.schemas.user import UserInsert, UserSelect
from app.db import SessionLocal
from app.routers import users
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db import Base, engine
    from app.models.user import User
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
