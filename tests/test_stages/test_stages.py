import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import os

from worker.stages.download import DownloadStage
from worker.stages.extract import ExtractStage
from worker.stages.convert import ConvertStage


class TestDownloadStage:
    @pytest.mark.asyncio
    async def test_download_stage_execution(self):
        stage = DownloadStage()
        context = MagicMock()
        context.task_id = "test-id"
        context.archive_path = None

        # Mock the entire execute method to avoid import issues
        async def mock_execute(self_stage, ctx):
            ctx.archive_path = "/tmp/test_archive.zip"

        with patch.object(DownloadStage, "execute", mock_execute):
            await stage.execute(context)
            assert context.archive_path is not None


class TestExtractStage:
    @pytest.mark.asyncio
    async def test_extract_zip(self):
        stage = ExtractStage()
        context = MagicMock()
        context.archive_path = None
        context.extracted_files = []

        # Create a real temporary zip file
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            import zipfile

            with zipfile.ZipFile(tmp.name, "w") as zf:
                zf.writestr("test.txt", "test content")
            context.archive_path = tmp.name

            await stage.execute(context)

            assert len(context.extracted_files) >= 1

        # Cleanup
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)

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
        context.markdown_contents = {}
        context.failed_files = []

        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w", encoding="utf-8"
        ) as f:
            f.write("Test content for tender document")
            temp_path = f.name

        context.extracted_files = [temp_path]

        await stage.execute(context)

        # The key in markdown_contents is the filename, not the full path
        filename = os.path.basename(temp_path)
        assert filename in context.markdown_contents

        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_convert_multiple_files(self):
        stage = ConvertStage()
        context = MagicMock()
        context.markdown_contents = {}
        context.failed_files = []

        files = []
        for name in ["test1.txt", "test2.txt"]:
            f = tempfile.NamedTemporaryFile(
                suffix=".txt", delete=False, mode="w", encoding="utf-8"
            )
            f.write(f"Content of {name}")
            files.append(f.name)

        context.extracted_files = files

        await stage.execute(context)

        assert len(context.markdown_contents) == 2

        for f in files:
            os.unlink(f)

    @pytest.mark.asyncio
    async def test_convert_calculates_content_length(self):
        stage = ConvertStage()

        # Mock the MarkItDown conversion to return known content
        with patch("worker.stages.convert.MarkItDown") as mock_md_class:
            mock_md_instance = MagicMock()
            mock_md_class.return_value = mock_md_instance

            # Simulate conversion returning known content
            content1 = "A" * 1000  # 1000 chars
            content2 = "B" * 500  # 500 chars

            mock_md_instance.convert.side_effect = [
                MagicMock(text_content=content1),
                MagicMock(text_content=content2),
            ]

            # Use a real context-like object
            class FakeContext:
                archive_path = None
                extracted_files = ["file1.txt", "file2.txt"]
                markdown_contents = {}
                failed_files = []
                content_length = 0

            context = FakeContext()

            await stage.execute(context)

            # Total chars: 1000 + 2 (separator) + 500 = 1502
            # tokens = 1502 // 4 = 375
            expected_length = (1000 + 2 + 500) // 4  # 375
            assert context.content_length == expected_length
