import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from worker.pipeline import ExtractionPipeline, PipelineContext


class TestPipelineContext:
    def test_initialization(self):
        ctx = PipelineContext("test-task-id")
        assert ctx.task_id == "test-task-id"
        assert ctx.archive_path is None
        assert ctx.extracted_files == []
        assert ctx.markdown_contents == {}
        assert ctx.extraction_result is None

    def test_context_attributes(self):
        ctx = PipelineContext("test-id")
        ctx.archive_path = "/tmp/archive.zip"
        ctx.extracted_files = ["file1.txt", "file2.pdf"]
        ctx.markdown_contents = {"file1.txt": "content1"}
        ctx.extraction_result = {"result": "data"}

        assert ctx.archive_path == "/tmp/archive.zip"
        assert len(ctx.extracted_files) == 2
        assert ctx.markdown_contents["file1.txt"] == "content1"
        assert ctx.extraction_result == {"result": "data"}


class TestExtractionPipeline:
    @pytest.mark.asyncio
    async def test_pipeline_stages_order(self):
        pipeline = ExtractionPipeline()

        stage_names = [stage.__class__.__name__ for stage in pipeline.stages]
        expected = [
            "DownloadStage",
            "ExtractStage",
            "ConvertStage",
            "ExtractLLMStage",
            "SaveStage",
        ]

        assert stage_names == expected

    @pytest.mark.asyncio
    async def test_pipeline_execute_order(self):
        pipeline = ExtractionPipeline()

        with (
            patch("worker.pipeline.get_task_by_id") as mock_get_task,
            patch("worker.stages.download.DownloadStage.execute") as mock_download,
            patch("worker.stages.extract.ExtractStage.execute") as mock_extract,
            patch("worker.stages.convert.ConvertStage.execute") as mock_convert,
            patch("worker.stages.extract_llm.ExtractLLMStage.execute") as mock_llm,
            patch("worker.stages.save.SaveStage.execute") as mock_save,
        ):
            mock_get_task.return_value = {
                "id": "test-id",
                "archive_url": "https://example.com/archive.zip",
                "status": "pending",
            }

            mock_download.return_value = None
            mock_extract.return_value = None
            mock_convert.return_value = None
            mock_llm.return_value = None
            mock_save.return_value = None

            context = PipelineContext("test-id")
            context.archive_path = "/tmp/archive.zip"

            mock_ctx = MagicMock()
            mock_ctx.markdown_contents = {"file1": "content"}
            mock_ctx.extraction_result = {"result": "data"}

            with patch.object(
                pipeline,
                "stages",
                [
                    create_mock_stage("download", mock_download),
                    create_mock_stage("extract", mock_extract),
                    create_mock_stage("convert", mock_convert),
                    create_mock_stage("llm", mock_llm),
                    create_mock_stage("save", mock_save),
                ],
            ):
                pipeline.stages[0].execute = mock_download
                pipeline.stages[1].execute = mock_extract
                pipeline.stages[2].execute = mock_convert
                pipeline.stages[3].execute = mock_llm
                pipeline.stages[4].execute = mock_save

                result = await pipeline.execute("test-id")

            assert mock_download.called
            assert mock_extract.called
            assert mock_convert.called
            assert mock_llm.called
            assert mock_save.called


def create_mock_stage(name, mock_method):
    stage = MagicMock()
    stage.__class__.__name__ = f"{name.capitalize()}Stage"
    stage.execute = mock_method
    return stage
