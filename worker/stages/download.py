import logging
import httpx
import tempfile
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class DownloadStage:
    """Download archive from URL"""

    async def execute(self, context):
        from worker.tasks import get_task_by_id

        task = await get_task_by_id(context.task_id)
        archive_url = task["archive_url"]

        logger.info(f"Downloading archive from: {archive_url}")

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.get(
                archive_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
                },
                follow_redirects=True,
            )
            response.raise_for_status()

        suffix = self._get_suffix(archive_url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(response.content)
            context.archive_path = tmp.name

        logger.info(f"Archive downloaded to: {context.archive_path}")

    def _get_suffix(self, url: str) -> str:
        if url.endswith(".zip"):
            return ".zip"
        elif url.endswith(".tar.gz") or url.endswith(".tgz"):
            return ".tar.gz"
        elif url.endswith(".7z"):
            return ".7z"
        elif url.endswith(".rar"):
            return ".rar"
        return ".zip"
