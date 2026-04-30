from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
import json

from api.database import get_db, ExtractionTask
from api.models import ExtractionCreate, ExtractionResponse, ExtractionStatusResponse

router = APIRouter(prefix="/tenders", tags=["tenders"])

TOPIC = "extraction-tasks"

_producer = None


def get_producer():
    global _producer
    if _producer is None:
        from kafka import KafkaProducer
        from api.config import settings

        _producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return _producer


@router.post("/extraction", response_model=ExtractionResponse)
async def create_extraction_task(
    data: ExtractionCreate, db: AsyncSession = Depends(get_db)
):
    task_id = str(uuid4())
    task = ExtractionTask(
        id=task_id,
        tender_id=data.tender_id,
        archive_url=data.archive_url,
        model=data.model,
        status="pending",
        stage_progress={},
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    producer = get_producer()
    message = {"task_id": task_id, "model": data.model, "tender_id": data.tender_id}
    future = producer.send(TOPIC, message)
    future.get(timeout=10)

    return task


@router.get("/extraction/{task_id}", response_model=ExtractionStatusResponse)
async def get_extraction_status(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExtractionTask).where(ExtractionTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return ExtractionStatusResponse(
        task_id=task.id,
        tender_id=task.tender_id,
        status=task.status,
        current_stage=task.current_stage,
        result_json=task.result_json,
        failed_files=task.failed_files,
        summary_text=task.summary_text,
        procurement_request_url=task.procurement_request_url,
        error_message=task.error_message,
    )
