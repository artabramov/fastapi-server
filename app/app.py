from fastapi import FastAPI
from app.routers import user_routers
from contextlib import asynccontextmanager
from app.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_routers.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
