import logging
import os
import shutil
import tempfile
import time
from datetime import datetime, timedelta

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from api.config import settings
from api.database import ExtractionTask

logger = logging.getLogger(__name__)


def _cleanup_old_db_records(retention_days: int):
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    engine = create_engine(settings.database_url_sync)
    try:
        with Session(engine) as session:
            stmt = delete(ExtractionTask).where(
                ExtractionTask.status.in_(["completed", "failed"]),
                ExtractionTask.updated_at < cutoff,
            )
            result = session.execute(stmt)
            session.commit()
            if result.rowcount:
                logger.info(
                    f"Cleaned {result.rowcount} old DB records (retention: {retention_days}d)"
                )
    finally:
        engine.dispose()


def _cleanup_orphaned_temps(orphan_hours: int):
    temp_dir = tempfile.gettempdir()
    cutoff = time.time() - orphan_hours * 3600
    archive_suffixes = {".zip", ".7z", ".rar", ".tar", ".tar.gz", ".tgz"}

    for item in os.listdir(temp_dir):
        if not item.startswith("tmp"):
            continue
        item_path = os.path.join(temp_dir, item)
        try:
            if os.stat(item_path).st_mtime > cutoff:
                continue
        except OSError:
            continue

        try:
            if os.path.isfile(item_path):
                if any(item.endswith(s) for s in archive_suffixes):
                    os.unlink(item_path)
                    logger.info(f"Cleaned orphaned temp file: {item_path}")
            elif os.path.isdir(item_path) and not item.startswith("tmp."):
                shutil.rmtree(item_path)
                logger.info(f"Cleaned orphaned temp dir: {item_path}")
        except (FileNotFoundError, PermissionError):
            pass


def periodic_cleanup():
    interval_minutes = settings.cleanup_interval_minutes
    retention_days = settings.cleanup_db_retention_days
    orphan_hours = int(os.getenv("CLEANUP_ORPHAN_HOURS", "24"))

    logger.info(
        f"Periodic cleanup started (interval={interval_minutes}m, "
        f"db_retention={retention_days}d, orphan_hours={orphan_hours}h)"
    )

    while True:
        try:
            _cleanup_old_db_records(retention_days)
            _cleanup_orphaned_temps(orphan_hours)
        except Exception as e:
            logger.error(f"Periodic cleanup cycle failed: {e}")

        time.sleep(interval_minutes * 60)
