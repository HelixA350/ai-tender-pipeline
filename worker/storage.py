import logging
import os

from api.config import settings, OUTPUT_DIR

logger = logging.getLogger(__name__)


def save_file(filename: str, content: bytes) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    logger.info(f"Saved file {filename} to {OUTPUT_DIR}")
    return file_path


def get_file_path(filename: str) -> str:
    return os.path.join(OUTPUT_DIR, filename)
