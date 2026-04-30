import logging
import asyncio
from sqlalchemy import update

from api.config import settings
from api.database import ExtractionTask

logger = logging.getLogger(__name__)


class SaveStage:
    """Save extraction result to database (background task with retry)"""

    async def execute(self, context):
        asyncio.create_task(self._save_async(context))
        logger.info("Save task dispatched to background")

    async def _save_async(self, context):
        from sqlalchemy.ext.asyncio import (
            create_async_engine,
            AsyncSession,
            async_sessionmaker,
        )

        engine = create_async_engine(settings.database_url, echo=False)
        async_session = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        for attempt in range(3):
            try:
                async with async_session() as session:
                    stmt = (
                        update(ExtractionTask)
                        .where(ExtractionTask.id == context.task_id)
                        .values(
                            status="completed",
                            current_stage="save",
                            stage_progress={
                                "download": True,
                                "extract": True,
                                "convert": True,
                                "llm": True,
                                "save": True,
                            },
                            failed_files=context.failed_files,
                        )
                    )
                    await session.execute(stmt)
                    await session.commit()

                logger.info(f"Result saved for task {context.task_id}")
                break

            except Exception as e:
                logger.warning(f"DB save attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(1)
                else:
                    logger.error(
                        f"Failed to save result for task {context.task_id}: {e}"
                    )

        await engine.dispose()
