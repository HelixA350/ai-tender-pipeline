import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from worker.stages.download import DownloadStage
from worker.stages.extract import ExtractStage
from worker.stages.convert import ConvertStage
from worker.stages.extract_llm import ExtractLLMStage
from worker.stages.save import SaveStage

logger = logging.getLogger(__name__)


class PipelineContext:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.archive_path: str | None = None
        self.extracted_files: list[str] = []
        self.markdown_contents: dict[str, str] = {}
        self.extraction_result: dict | None = None
        self.failed_files: list[str] = []


async def update_task_status(
    task_id: str,
    status: str,
    result: dict | None = None,
    error: str | None = None,
    failed_files: list | None = None,
):
    from sqlalchemy import update
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        AsyncSession,
        async_sessionmaker,
    )
    from api.config import settings
    from api.database import ExtractionTask

    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        values = {
            "status": status,
            "current_stage": status,
            "updated_at": datetime.utcnow(),
        }
        if result is not None:
            values["result_json"] = result
        if error is not None:
            values["error_message"] = error
        if failed_files is not None:
            values["failed_files"] = failed_files

        stmt = (
            update(ExtractionTask)
            .where(ExtractionTask.id == UUID(task_id))
            .values(**values)
        )
        await session.execute(stmt)
        await session.commit()

    await engine.dispose()


class ExtractionPipeline:
    def __init__(self):
        self.stages = [
            DownloadStage(),
            ExtractStage(),
            ConvertStage(),
            ExtractLLMStage(),
            SaveStage(),
        ]

    async def execute(self, task_id: str) -> dict:
        context = PipelineContext(task_id)

        # Run stages 1-4 (Download, Extract, Convert, LLM)
        for stage in self.stages[:-1]:
            stage_name = stage.__class__.__name__
            logger.info(f"Executing stage: {stage_name} for task {task_id}")

            try:
                await stage.execute(context)
                logger.info(f"Stage {stage_name} completed for task {task_id}")
            except Exception as e:
                logger.error(f"Stage {stage_name} failed for task {task_id}: {e}")
                raise

        # Update status to "completed" BEFORE background save
        logger.info(f"Updating task {task_id} status to completed")
        await update_task_status(
            task_id,
            "completed",
            context.extraction_result,
            failed_files=context.failed_files,
        )

        # Run SaveStage (background save - doesn't block)
        save_stage = SaveStage()
        await save_stage.execute(context)

        return context.extraction_result or {}


class SyncPipelineWrapper:
    """Wrapper to run async pipeline from Celery sync tasks."""

    def __init__(self):
        self.pipeline = ExtractionPipeline()

    def execute_sync(self, task_id: str) -> dict:
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(self.pipeline.execute(task_id))
        except RuntimeError:
            return asyncio.run(self.pipeline.execute(task_id))
