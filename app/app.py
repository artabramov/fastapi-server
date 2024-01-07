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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create SQLAlchemy tables."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan, root_path="/api/v1")
app.include_router(user_routers.router)
log = get_log()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Do not spend resources if debug is disabled.
    if log.level <= log.root.level:
        set_context_var("uuid", str(uuid4()))
        start_time = time()
        log.debug("Request received, method=%s, url=%s, headers=%s" % (
            request.method, request.url, str(request.headers.raw)))

    response = await call_next(request)

    # Do not spend resources if debug is disabled
    if log.level <= log.root.level:
        elapsed_time = time() - start_time
        response.headers["X-Process-Time"] = str(elapsed_time)

        # Save the data to a list and use iterate_in_threadpool to initiate the iterator again for response.
        # https://stackoverflow.com/questions/71882419/fastapi-how-to-get-the-response-body-in-middleware
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))

        log.debug("Response sent, elapsed time=%s, status_code=%s, headers=%s, response_body=%s" % (
            elapsed_time, response.status_code, str(response.headers.raw), response_body[0].decode()))

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
