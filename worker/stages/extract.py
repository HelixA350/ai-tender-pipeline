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

MAX_NESTING_DEPTH = 5


class ExtractStage:
    """Extract archive contents"""

    async def execute(self, context):
        import tempfile

        archive_path = Path(context.archive_path)
        ext = self._get_ext(archive_path)

        logger.info(f"Extracting archive: {archive_path}")

        temp_dir = tempfile.mkdtemp()

        try:
            self._extract_archive(archive_path, temp_dir, depth=0)
        except Exception as e:
            raise ValueError(f"Failed to extract archive: {e}")

        extracted = []
        for item in Path(temp_dir).rglob("*"):
            if item.is_file():
                extracted.append(str(item))

        context.extracted_files = extracted
        logger.info(f"Extracted {len(extracted)} files")

    def _get_ext(self, path: Path) -> str:
        ext = path.suffix.lower()
        if ext == ".gz" and path.stem.endswith(".tar"):
            return ".tar.gz"
        return ext

    def _is_archive(self, path: Path) -> bool:
        ext = self._get_ext(path)
        return ext in SUPPORTED_ARCHIVES

    def _extract_archive(self, archive_path: Path, temp_dir: str, depth: int):
        ext = self._get_ext(archive_path)

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

        self._extract_nested_archives(temp_dir, depth + 1)

    def _extract_nested_archives(self, temp_dir: str, depth: int):
        if depth >= MAX_NESTING_DEPTH:
            logger.info(
                f"Max nesting depth {MAX_NESTING_DEPTH} reached, stopping extraction"
            )
            return

        temp_path = Path(temp_dir)
        while True:
            archives = [
                f for f in temp_path.rglob("*") if f.is_file() and self._is_archive(f)
            ]
            if not archives:
                break

            for archive in archives:
                logger.info(f"Extracting nested archive: {archive}")
                archive_dir = archive.parent
                archive_stem = archive.stem

                extracted_files_before = set(
                    f.name for f in archive_dir.iterdir() if f.is_file()
                )

                self._extract_archive(archive, str(archive_dir), depth)

                if archive.exists():
                    try:
                        archive.unlink()
                    except FileNotFoundError:
                        pass

                extracted_files_after = set(
                    f.name for f in archive_dir.iterdir() if f.is_file()
                )
                new_files = extracted_files_after - extracted_files_before

                for item in archive_dir.rglob("*"):
                    if item.is_file() and item.suffix.lower() in {
                        ".zip",
                        ".tar",
                        ".gz",
                        ".7z",
                        ".rar",
                        ".tgz",
                    }:
                        continue
                    if archive_stem not in item.name and item.parent == archive_dir:
                        new_name = f"{archive_stem}_{item.name}"
                        new_path = item.parent / new_name
                        try:
                            if not new_path.exists():
                                item.rename(new_path)
                        except FileNotFoundError:
                            pass
