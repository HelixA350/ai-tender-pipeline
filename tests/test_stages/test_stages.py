import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

from worker.stages.download import DownloadStage
from worker.stages.extract import ExtractStage
from worker.stages.convert import ConvertStage


class TestDownloadStage:
    @pytest.mark.asyncio
    async def test_download_stage_execution(self):
        stage = DownloadStage()
        context = MagicMock()
        context.task_id = "test-id"

        with (
            patch("worker.stages.download.get_task_by_id") as mock_get_task,
            patch("worker.stages.download.httpx.AsyncClient") as mock_client,
        ):
            mock_get_task.return_value = {
                "id": "test-id",
                "archive_url": "https://example.com/archive.zip",
            }

            mock_response = MagicMock()
            mock_response.content = b"fake archive data"
            mock_response.raise_for_status = MagicMock()

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            await stage.execute(context)

            assert context.archive_path is not None


class TestExtractStage:
    @pytest.mark.asyncio
    async def test_extract_zip(self):
        stage = ExtractStage()
        context = MagicMock()
        context.archive_path = str(
            Path(__file__).parent.parent / "test_data" / "test.zip"
        )

        import tempfile
        import zipfile

        test_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        with zipfile.ZipFile(test_zip, "w") as zf:
            zf.writestr("test.txt", "test content")
        context.archive_path = test_zip.name

        await stage.execute(context)

        assert len(context.extracted_files) >= 1

        import os

        os.unlink(test_zip.name)

    @pytest.mark.asyncio
    async def test_extract_unsupported_format(self):
        stage = ExtractStage()
        context = MagicMock()
        context.archive_path = "/tmp/archive.unknown"

        with pytest.raises(ValueError, match="Unsupported archive format"):
            await stage.execute(context)


class TestConvertStage:
    @pytest.mark.asyncio
    async def test_convert_txt_file(self):
        stage = ConvertStage()
        context = MagicMock()

        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("Test content for tender document")
            temp_path = f.name

        context.extracted_files = [temp_path]

        await stage.execute(context)

        assert "test.txt" in context.markdown_contents

        import os

        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_convert_multiple_files(self):
        stage = ConvertStage()
        context = MagicMock()

        import tempfile

        files = []

        for name in ["test1.txt", "test2.txt"]:
            f = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w")
            f.write(f"Content of {name}")
            files.append(f.name)

        context.extracted_files = files

        await stage.execute(context)

        assert len(context.markdown_contents) == 2

        import os

        for f in files:
            os.unlink(f)
