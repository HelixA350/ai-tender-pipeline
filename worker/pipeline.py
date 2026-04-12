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
from worker.stages.create_procurement_request import CreateProcurementRequestStage

logger = logging.getLogger(__name__)


async def run_stage(stage, context, task_id: str):
    stage_name = stage.__class__.__name__
    logger.info(f"Executing stage: {stage_name} for task {task_id}")

    try:
        await stage.execute(context)
        logger.info(f"Stage {stage_name} completed for task {task_id}")
    except Exception as e:
        logger.error(f"Stage {stage_name} failed for task {task_id}: {e}")
        raise


async def try_run_stage(stage, context, task_id: str, stage_key: str):
    stage_name = stage.__class__.__name__
    max_retries = 3

    if context.extraction_result is None:
        context.extraction_result = {}

    context.extraction_result.setdefault("stage_errors", {})

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Executing stage: {stage_name} for task {task_id} (attempt {attempt}/{max_retries})"
            )
            await stage.execute(context)
            logger.info(f"Stage {stage_name} completed for task {task_id}")
            return True
        except Exception as e:
            logger.warning(
                f"Stage {stage_name} failed for task {task_id} (attempt {attempt}/{max_retries}): {e}"
            )
            if attempt == max_retries:
                context.extraction_result["stage_errors"][stage_key] = str(e)
                return False
            await asyncio.sleep(2)

    return False


def extract_summary_text(context: "PipelineContext") -> str:
    if not context.extraction_result or not context.extraction_result.get("summary"):
        return ""

    from worker.schemas.tender_schema import SemanticSummary

    summary_data = context.extraction_result["summary"]
    if not summary_data:
        return ""

    try:
        summary_obj = SemanticSummary(**summary_data)
        return summary_obj.to_text()
    except Exception as e:
        logger.warning(f"Failed to extract summary_text: {e}")
        return ""


class PipelineContext:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.archive_path: str | None = None
        self.extracted_files: list[str] = []
        self.markdown_contents: dict[str, str] = {}
        self.extraction_result: dict | None = None
        self.failed_files: list[str] = []
        self.summary_text: str = ""
        self.procurement_request_url: str | None = None


async def update_task_status(
    task_id: str,
    status: str,
    result: dict | None = None,
    error: str | None = None,
    failed_files: list | None = None,
    summary_text: str | None = None,
    procurement_request_url: str | None = None,
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
        if summary_text is not None:
            values["summary_text"] = summary_text
        elif summary_text == "":
            values["summary_text"] = ""
        if procurement_request_url is not None:
            values["procurement_request_url"] = procurement_request_url

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
        self.download_stage = DownloadStage()
        self.extract_stage = ExtractStage()
        self.convert_stage = ConvertStage()
        self.llm_stage = ExtractLLMStage()
        self.save_stage = SaveStage()
        self.procurement_request_stage = CreateProcurementRequestStage()

    async def execute(self, task_id: str) -> dict:
        context = PipelineContext(task_id)

        await run_stage(self.download_stage, context, task_id)
        await run_stage(self.extract_stage, context, task_id)
        await run_stage(self.convert_stage, context, task_id)
        await run_stage(self.llm_stage, context, task_id)

        procurement_items = (
            context.extraction_result.get("procurement_items", [])
            if context.extraction_result
            else []
        )
        if procurement_items:
            await try_run_stage(
                self.procurement_request_stage,
                context,
                task_id,
                "create_procurement_request",
            )

        logger.info(f"Updating task {task_id} status to completed")

        context.summary_text = extract_summary_text(context)

        await update_task_status(
            task_id,
            "completed",
            context.extraction_result,
            failed_files=context.failed_files,
            summary_text=context.summary_text,
            procurement_request_url=context.procurement_request_url,
        )

        await self.save_stage.execute(context)

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
