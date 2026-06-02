import asyncio
import logging
import os
import shutil
from datetime import datetime

from worker.stages.download import DownloadStage
from worker.stages.extract import ExtractStage
from worker.stages.convert import ConvertStage
from worker.stages.extract_llm import ExtractLLMStage
from worker.stages.save import SaveStage
from worker.stages.rag_extraction import RAGExtractionStage

logger = logging.getLogger(__name__)


async def run_stage(stage, context, task_id: str, model: str = None):
    stage_name = stage.__class__.__name__
    logger.info(f"Executing stage: {stage_name} for task {task_id}")

    try:
        if model is not None:
            await stage.execute(context, model)
        else:
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


class PipelineContext:
    def __init__(self, task_id: str, model: str = "openai", tender_id: str = None):
        self.task_id = task_id
        self.model = model
        self.tender_id = tender_id or task_id
        self.archive_path: str | None = None
        self.temp_extract_dir: str | None = None
        self.extracted_files: list[str] = []
        self.markdown_contents: dict[str, str] = {}
        self.extraction_result: dict | None = None
        self.failed_files: list[str] = []
        self.summary_text: str = ""
        self.content_length: int = 0


async def update_task_status(
    task_id: str,
    status: str,
    result: dict | None = None,
    error: str | None = None,
    failed_files: list | None = None,
    summary_text: str | None = None,
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

        stmt = (
            update(ExtractionTask).where(ExtractionTask.id == task_id).values(**values)
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

    async def execute(
        self, task_id: str, model: str = "openai", tender_id: str = None
    ) -> dict:
        context = PipelineContext(task_id, model, tender_id)

        try:
            await run_stage(self.download_stage, context, task_id)
            await run_stage(self.extract_stage, context, task_id)
            await run_stage(self.convert_stage, context, task_id)

            # Choose extraction strategy based on content length
            if context.content_length >= 50000:
                logger.info(
                    f"Content length {context.content_length} >= 50000, using RAG extraction"
                )
                rag_stage = RAGExtractionStage()
                await run_stage(rag_stage, context, task_id, model)
            else:
                logger.info(
                    f"Content length {context.content_length} < 50000, using standard LLM extraction"
                )
                await run_stage(self.llm_stage, context, task_id, model)

            logger.info(f"Updating task {task_id} status to completed")

            # Build new result_json structure
            result_json = self._build_result_json(context)

            await update_task_status(
                task_id,
                "completed",
                result_json,
                failed_files=context.failed_files,
                summary_text=result_json.get("summary_text", ""),
            )

            await self.save_stage.execute(context)

            return result_json

        finally:
            self._cleanup_temp_files(context, task_id)

    def _cleanup_temp_files(self, context: PipelineContext, task_id: str):
        if context.archive_path and os.path.exists(context.archive_path):
            try:
                os.unlink(context.archive_path)
                logger.info(f"Deleted temp archive: {context.archive_path} for task {task_id}")
            except Exception as e:
                logger.warning(f"Failed to delete temp archive {context.archive_path}: {e}")

        if context.temp_extract_dir and os.path.exists(context.temp_extract_dir):
            try:
                shutil.rmtree(context.temp_extract_dir)
                logger.info(f"Deleted temp extract dir: {context.temp_extract_dir} for task {task_id}")
            except Exception as e:
                logger.warning(f"Failed to delete temp extract dir {context.temp_extract_dir}: {e}")

    def _build_result_json(self, context: PipelineContext) -> dict:
        from worker.schemas.tender_schema import TenderSchemaShort, SemanticSummary

        # Маппинг полей на русский
        FIELD_MAPPING = {
            "no": "№",
            "request_number": "Запрос №",
            "article": "Партномер/артикул",
            "name": "Наименование",
            "qty": "Кол-во",
            "unit": "Ед.изм",
            "brand": "Бренд",
            "manufacturer": "Производитель",
            "equipment_model": "Модель оборудования",
            "serial_number": "Серийный №",
            "drawing": "Чертеж",
            "drawing_position": "Позиция на чертеже",
            "material": "Материал",
            "comments": "Комментарии",
        }

        if not context.extraction_result:
            return {
                "tender_id": context.tender_id,
                "summary_text": "",
                "error_message": "No extraction result",
                "status": "failed",
                "table_tender": [],
            }

        try:
            tender_short = TenderSchemaShort(**context.extraction_result)

            summary_text = ""
            if tender_short.summary:
                summary_text = tender_short.summary.to_text()

            # Маппинг procurement_items с переводом полей
            procurement_items = []
            if tender_short.procurement_items:
                for item in tender_short.procurement_items:
                    item_dict = item.model_dump()
                    mapped_item = {
                        FIELD_MAPPING.get(k, k): v for k, v in item_dict.items()
                    }
                    procurement_items.append(mapped_item)

            result = {
                "tender_id": context.tender_id,
                "summary_text": summary_text,
                "error_message": "",
                "status": "completed",
                "table_tender": procurement_items,
            }
            return result

        except Exception as e:
            logger.error(f"Failed to build result_json: {e}")
            return {
                "tender_id": context.tender_id,
                "summary_text": "",
                "error_message": str(e),
                "status": "failed",
                "table_tender": [],
            }


class SyncPipelineWrapper:
    """Wrapper to run async pipeline from Celery sync tasks."""

    def __init__(self):
        self.pipeline = ExtractionPipeline()

    def execute_sync(
        self, task_id: str, model: str = "openai", tender_id: str = None
    ) -> dict:
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(
                self.pipeline.execute(task_id, model, tender_id)
            )
        except RuntimeError:
            return asyncio.run(self.pipeline.execute(task_id, model, tender_id))
