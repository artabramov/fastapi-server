"""Main module."""

from time import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.session import Base, engine
from app.routers import user_routers, collection_routers
from app.context import set_context_var
from app.log import get_log
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from app.dotenv import get_config
from app.managers.file_manager import FileManager

config = get_config()
log = get_log()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create SQLAlchemy tables."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_routers.router, prefix=config.API_PREFIX)
app.include_router(collection_routers.router, prefix=config.API_PREFIX)

mfa_path = FileManager.path_join(config.APPDATA_PATH, config.MFA_DIR)
app.mount("/mfa", StaticFiles(directory=mfa_path, html=False), name=mfa_path)

userpic_path = FileManager.path_join(config.APPDATA_PATH, config.USERPIC_DIR)
app.mount("/userpics", StaticFiles(directory=userpic_path, html=False), name=userpic_path)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Log request and response."""
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
    """Process validation error."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": e.errors()}),
    )
