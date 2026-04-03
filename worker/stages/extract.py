import logging
import zipfile
import tarfile
import py7zr
import rarfile
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_ARCHIVES = {
    ".zip": "zip",
    ".tar": "tar",
    ".tar.gz": "tar",
    ".tgz": "tar",
    ".7z": "7z",
    ".rar": "rar",
}


class ExtractStage:
    """Extract archive contents"""

    async def execute(self, context):
        import tempfile

        archive_path = Path(context.archive_path)
        ext = archive_path.suffix.lower()

        if ext == ".gz" and archive_path.stem.endswith(".tar"):
            ext = ".tar.gz"

        logger.info(f"Extracting archive: {archive_path}")

        temp_dir = tempfile.mkdtemp()

        try:
            if ext == ".zip":
                with zipfile.ZipFile(archive_path, "r") as zf:
                    zf.extractall(temp_dir)
            elif ext in (".tar", ".tar.gz", ".tgz"):
                with tarfile.open(archive_path, "r:*") as tf:
                    tf.extractall(temp_dir)
            elif ext == ".7z":
                with py7zr.SevenZipFile(archive_path, "r") as zf:
                    zf.extractall(temp_dir)
            elif ext == ".rar":
                with rarfile.RarFile(archive_path, "r") as rf:
                    rf.extractall(temp_dir)
            else:
                raise ValueError(f"Unsupported archive format: {ext}")
        except Exception as e:
            raise ValueError(f"Failed to extract archive: {e}")

        extracted = []
        for item in Path(temp_dir).rglob("*"):
            if item.is_file():
                extracted.append(str(item))

        context.extracted_files = extracted
        logger.info(f"Extracted {len(extracted)} files")
