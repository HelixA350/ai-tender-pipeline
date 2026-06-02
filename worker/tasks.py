import asyncio
import logging
import json
import threading

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from api.config import settings
from worker.pipeline import SyncPipelineWrapper
from worker.cleanup_service import periodic_cleanup
from api.database import ExtractionTask

logger = logging.getLogger(__name__)

TOPIC = "extraction-tasks"
RESULT_TOPIC = "extraction-results"
GROUP_ID = "workers"
BOOTSTRAP_SERVERS = settings.kafka_bootstrap_servers

pipeline = SyncPipelineWrapper()

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

_producer = None


def get_result_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return _producer


async def get_task_by_id(task_id: str):
    async with async_session() as session:
        result = await session.execute(
            select(ExtractionTask).where(ExtractionTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        return {
            "id": task.id,
            "tender_id": task.tender_id,
            "archive_url": task.archive_url,
            "status": task.status,
            "stage_progress": task.stage_progress or {},
            "current_stage": task.current_stage,
        }


async def update_task_stage(task_id: str, stage: str, progress: dict):
    async with async_session() as session:
        stmt = (
            update(ExtractionTask)
            .where(ExtractionTask.id == task_id)
            .values(current_stage=stage, stage_progress=progress, status="processing")
        )
        await session.execute(stmt)
        await session.commit()


async def process_task(task_id: str, model: str = "chatgpt", tender_id: str = None, base_url: str = None):
    logger.info(
        f"Processing extraction task: {task_id} with model: {model}, tender_id: {tender_id}, base_url: {base_url}"
    )

    try:
        result = await get_task_by_id(task_id)

        if result["status"] == "completed":
            logger.info(f"Task {task_id} already completed")
            return {"status": "completed"}

        progress = result.get("stage_progress", {})

        if not progress.get("download"):
            await update_task_stage(task_id, "download", {**progress, "download": True})

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

        extraction_result = pipeline.execute_sync(task_id, model, tender_id)

        # Send result to Kafka for webhook delivery
        producer = get_result_producer()
        message = {
            "result_json": extraction_result,
            "base_url": base_url or "",
        }
        future = producer.send(RESULT_TOPIC, message)
        future.get(timeout=10)

        return {"status": "completed", "result": extraction_result}

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")

        async with async_session() as session:
            stmt = (
                update(ExtractionTask)
                .where(ExtractionTask.id == task_id)
                .values(status="failed", error_message=str(e))
            )
            await session.execute(stmt)
            await session.commit()

        raise


def main():
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    logger.info("Periodic cleanup thread started")

    logger.info(f"Starting Kafka consumer for topic '{TOPIC}'...")

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    logger.info(f"Consumer started, listening to {TOPIC}")

    for message in consumer:
        data = json.loads(message.value.decode("utf-8"))
        task_id = data["task_id"]
        model = data.get("model", "chatgpt")
        tender_id = data.get("tender_id", task_id)
        base_url = data.get("base_url", "")
        logger.info(
            f"Received task: {task_id} with model: {model}, tender_id: {tender_id}, base_url: {base_url}"
        )

        try:
            asyncio.run(process_task(task_id, model, tender_id, base_url))
            logger.info(f"Task {task_id} completed successfully")
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
