from time import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.session import Base, engine
from app.routers import user_routers
from app.context import set_context_var
from app.log import get_log
from uuid import uuid4
from starlette.concurrency import iterate_in_threadpool
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create SQLAlchemy tables."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
# app = FastAPI(lifespan=lifespan, root_path="/api/v1", openapi_url="/api/v1/openapi.json")
app.include_router(user_routers.router, prefix="/api/v1")
app.mount("/mfa", StaticFiles(directory="/memo/data/mfa", html=False), name="/memo/data/mfa")
log = get_log()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    set_context_var("uuid", str(uuid4()))
    start_time = time()

    log.debug("Request received, method=%s, url=%s, headers=%s" % (
        request.method, request.url, str(request.headers.raw)))

    response = await call_next(request)

    elapsed_time = time() - start_time
    response.headers["X-Process-Time"] = str(elapsed_time)

    log.debug("Response sent, elapsed time=%s, status_code=%s, headers=%s" % (
        elapsed_time, response.status_code, str(response.headers.raw)))

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, e: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": e.errors()}),
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}
