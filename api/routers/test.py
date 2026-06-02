import logging
import os

from fastapi import APIRouter, Form, HTTPException
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/test", tags=["test"])


class EmailMeta(BaseModel):
    message_id: str
    from_: str = Field(alias="from")
    to: list[str]
    subject: str
    received_at: str


class EmailBody(BaseModel):
    text: str | None = None
    html: str | None = None


@router.post("/email")
async def test_email(
    meta: str = Form(...),
    body: str = Form(...),
):
    meta_parsed = EmailMeta.model_validate_json(meta)
    body_parsed = EmailBody.model_validate_json(body)

    return {
        "status": "ok",
        "meta": meta_parsed.model_dump(by_alias=True),
        "body": body_parsed.model_dump(),
    }


@router.post("/card")
async def test_card():
    demo = {
        "title": "Поставка насосного оборудования",
        "request_type": "contest",
        "activity_direction": "SP",
        "description": "Поставка центробежных насосов для нужд нефтеперерабатывающего завода",
        "end_user": {
            "inn": "7701234567",
            "name": "АО Пример",
        },
        "source": "email",
        "lot_number": "Лот-001",
        "tkp_deadline": "2026-07-01",
        "tender_files_url": "https://example.com/tender/files",
        "scoring": {
            "pros": [
                "Стабильный заказчик с хорошей репутацией",
                "Конкурентная цена",
                "Долгосрочный контракт",
            ],
            "cons": [
                "Сжатые сроки поставки",
                "Сложные требования к качеству",
            ],
        },
    }

    webhook_url = os.getenv("TEST_WEBHOOK_URL")
    if not webhook_url:
        raise HTTPException(status_code=500, detail="TEST_WEBHOOK_URL is not set")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json=demo)
            return {
                "message": "я прислал на такой-то адрес вот такое содержимое",
                "sent_to_url": webhook_url,
                "sent_payload": demo,
                "webhook_status": resp.status_code,
                "webhook_response": resp.text,
            }
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Webhook send failed: {e}")
