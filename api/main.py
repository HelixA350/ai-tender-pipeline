import logging
import os

from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager

from starlette.middleware.base import BaseHTTPMiddleware

import httpx

from api.database import init_db
from api.routers import tenders, test
from api.config import LOG_FILE, OUTPUT_DIR, setup_logging
from api.models import ExtractionCreate

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

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
app.include_router(test.router)


@app.get("/health/")
async def health_check():
    return {"status": "healthy"}


@app.post("/poll")
async def poll_post(data: ExtractionCreate):
    if data.tender_id is None:
        raise HTTPException(status_code=400, detail="tender_id is required")

    callback_url = "https://tk.tandem-consult.ru/tender/index.php?action=callback"
    headers = {
        "Cookie": "BITRIX_SM2_TZ=Europe/Moscow; BITRIX_SM2_UIDL=a.faleev%40i-t-r.net; BITRIX_SM2_SALE_UID=530; BITRIX_SM2_LOGIN=a.faleev%40i-t-r.net; BITRIX_SM2_UIDD=g7r9cno17ltc0fh1ys2aonftxnr7mcw4; BITRIX_SM2_SOUND_LOGIN_PLAYED=Y; BITRIX_SM2_LAST_SETTINGS=; PHPSESSID=bBtWgG6FSb0S028EMmGKPCJXLdHte2m8; BITRIX_CONVERSION_CONTEXT_s1=%7B%22ID%22%3A2%2C%22EXPIRE%22%3A1777496340%2C%22UNIQUE%22%3A%5B%22conversion_visit_day%22%5D%7D",
        "Content-Type": "application/json",
    }
    callback_body = {
        "tender_id": data.tender_id,
        "summary_text": "Тестовая проверка: Данные успешно переданы из Postman. Анализ завершен.",
        "error_message": "",
        "status": "completed",
    }

    callback_status = None
    error = None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                callback_url, headers=headers, json=callback_body
            )
            callback_status = response.status_code
    except httpx.RequestError as e:
        error = str(e)

    return {
        "status": "callback sent"
        if callback_status and 200 <= callback_status < 300
        else "callback failed",
        "callback_status_code": callback_status,
        "tender_id": data.tender_id,
        "error": error,
    }
