from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import json

from api.database import get_db, ExtractionTask
from api.models import ExtractionCreate, ExtractionResponse, ExtractionStatusResponse

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.post("/extraction", response_model=ExtractionResponse)
async def create_extraction_task(
    data: ExtractionCreate, db: AsyncSession = Depends(get_db)
):
    task = ExtractionTask(
        tender_id=data.tender_id,
        archive_url=data.archive_url,
        status="pending",
        stage_progress={},
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    from worker.celery_app import celery_app

    celery_app.send_task("worker.tasks.process_extraction", args=[str(task.id)])

    return task


@router.get("/extraction/{task_id}", response_model=ExtractionStatusResponse)
async def get_extraction_status(task_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExtractionTask).where(ExtractionTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return ExtractionStatusResponse(
        task_id=task.id,
        status=task.status,
        current_stage=task.current_stage,
        result_json=task.result_json,
        failed_files=task.failed_files,
        summary_text=task.summary_text,
        procurement_request_url=task.procurement_request_url,
        error_message=task.error_message,
    )
