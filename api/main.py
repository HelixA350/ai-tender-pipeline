import logging

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from api.database import init_db
from api.routers import tenders
from api.config import LOG_FILE, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    yield


app = FastAPI(title="AI Tender Pipeline", version="1.0.0", lifespan=lifespan)

app.include_router(tenders.router)


@app.get("/health/")
async def health_check():
    return {"status": "healthy"}


logger = logging.getLogger(__name__)


@app.post("/ping")
async def ping(request: Request):
    body = await request.body()
    logger.info(f"PING - body: {body}")
    logger.info(f"PING - query_params: {dict(request.query_params)}")
    logger.info(f"PING - headers: {dict(request.headers)}")
    return {"status": "logged"}


@app.get("/file.log")
async def get_log():
    return FileResponse(LOG_FILE, media_type="text/plain", filename="file.log")
