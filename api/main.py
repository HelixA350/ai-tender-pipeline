import logging
import os
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from starlette.middleware.base import BaseHTTPMiddleware

import httpx

from api.database import init_db
from api.routers import tenders
from api.config import LOG_FILE, OUTPUT_DIR, setup_logging
from api.models import ExtractionResponse, ExtractionStatusResponse

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


async def _send_to_client_ip(server_ip: str, payload: dict):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(f"http://{server_ip}/", json=payload)
    except Exception:
        pass


@app.get("/poll")
async def poll_get(request: Request):
    result = ExtractionStatusResponse(
        task_id="poll-get-test-id",
        status="completed",
        current_stage="test",
        result_json={"test": "get-poll-result"},
        failed_files=[],
        summary_text="Test GET /poll result",
        procurement_request_url=None,
        error_message=None,
    )
    result_dict = result.model_dump()
    server_ip = request.client.host if request.client else "127.0.0.1"
    await _send_to_client_ip(server_ip, result_dict)
    return result


@app.post("/poll")
async def poll_post(request: Request):
    now = datetime.utcnow()
    result = ExtractionResponse(
        id="poll-post-test-id",
        tender_id="poll-test-tender",
        archive_url="http://test.url/archive.zip",
        model="openai",
        status="pending",
        current_stage=None,
        stage_progress={},
        result_json=None,
        failed_files=[],
        summary_text=None,
        error_message=None,
        retry_count=0,
        created_at=now,
        updated_at=now,
    )
    result_dict = result.model_dump()
    server_ip = request.client.host if request.client else "127.0.0.1"
    await _send_to_client_ip(server_ip, result_dict)
    return result
