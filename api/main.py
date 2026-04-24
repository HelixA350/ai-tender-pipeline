import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from starlette.middleware.base import BaseHTTPMiddleware

from api.database import init_db
from api.routers import tenders
from api.config import LOG_FILE, OUTPUT_DIR, setup_logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path == "/file.log":
            return await call_next(request)

        logger.info(f"Request: {request.method} {path}")
        logger.info(f"Request headers: {dict(request.headers)}")

        if request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            logger.info(f"Request body: {body}")

            async def receive():
                return {"type": "http.request", "body": body}

            request._receive = receive

        response = await call_next(request)

        logger.info(f"Response status: {response.status_code}")

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    await init_db()
    yield


app = FastAPI(title="AI Tender Pipeline", version="1.0.0", lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

app.include_router(tenders.router)


@app.get("/health/")
async def health_check():
    return {"status": "healthy"}


@app.post("/ping")
async def ping(request: Request):
    return {"status": "ok"}


@app.get("/file.log")
async def get_log():
    return FileResponse(LOG_FILE, media_type="text/plain", filename="file.log")
