import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from uuid import UUID

from worker.celery_app import celery_app
from worker.pipeline import SyncPipelineWrapper
from api.config import settings
from api.database import ExtractionTask

logger = logging.getLogger(__name__)

pipeline = SyncPipelineWrapper()


async def get_task_by_id(task_id: str) -> dict:
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        result = await session.execute(
            select(ExtractionTask).where(ExtractionTask.id == UUID(task_id))
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        return {
            "id": str(task.id),
            "tender_id": task.tender_id,
            "archive_url": task.archive_url,
            "status": task.status,
            "stage_progress": task.stage_progress or {},
            "current_stage": task.current_stage,
        }


async def update_task_stage(task_id: str, stage: str, progress: dict):
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        stmt = (
            update(ExtractionTask)
            .where(ExtractionTask.id == UUID(task_id))
            .values(current_stage=stage, stage_progress=progress, status="processing")
        )
        await session.execute(stmt)
        await session.commit()

    await engine.dispose()


@celery_app.task(bind=True, name="worker.tasks.process_extraction", max_retries=3)
def process_extraction(self, task_id: str):
    logger.info(f"Processing extraction task: {task_id}")

    import asyncio

    async def run():
        try:
            result = await get_task_by_id(task_id)

            if result["status"] == "completed":
                logger.info(f"Task {task_id} already completed")
                return {"status": "completed"}

            progress = result.get("stage_progress", {})

            if not progress.get("download"):
                await update_task_stage(
                    task_id, "download", {**progress, "download": True}
                )

            if not progress.get("extract"):
                await update_task_stage(
                    task_id, "extract", {**progress, "download": True, "extract": True}
                )

            if not progress.get("convert"):
                await update_task_stage(
                    task_id,
                    "convert",
                    {**progress, "download": True, "extract": True, "convert": True},
                )

            if not progress.get("llm"):
                await update_task_stage(
                    task_id,
                    "llm",
                    {
                        **progress,
                        "download": True,
                        "extract": True,
                        "convert": True,
                        "llm": True,
                    },
                )

            extraction_result = pipeline.execute_sync(task_id)

            return {"status": "completed", "result": extraction_result}

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")

            engine = create_async_engine(settings.database_url, echo=False)
            async_session = async_sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )

            async with async_session() as session:
                stmt = (
                    update(ExtractionTask)
                    .where(ExtractionTask.id == UUID(task_id))
                    .values(status="failed", error_message=str(e))
                )
                await session.execute(stmt)
                await session.commit()

            await engine.dispose()

            raise self.retry(exc=e, countdown=60)

    return asyncio.run(run())
