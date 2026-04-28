import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from worker.pipeline import ExtractionPipeline, PipelineContext, extract_summary_text
from worker.stages.rag_extraction import RAGExtractionStage


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
    async def test_pipeline_stages_attributes(self):
        pipeline = ExtractionPipeline()

        assert pipeline.download_stage.__class__.__name__ == "DownloadStage"
        assert pipeline.extract_stage.__class__.__name__ == "ExtractStage"
        assert pipeline.convert_stage.__class__.__name__ == "ConvertStage"
        assert pipeline.llm_stage.__class__.__name__ == "ExtractLLMStage"
        assert pipeline.save_stage.__class__.__name__ == "SaveStage"
        assert (
            pipeline.procurement_request_stage.__class__.__name__
            == "CreateProcurementRequestStage"
        )

    @pytest.mark.asyncio
    async def test_pipeline_execute_order_small_content(self):
        pipeline = ExtractionPipeline()

        with (
            patch.object(pipeline.download_stage, "execute") as mock_download,
            patch.object(pipeline.extract_stage, "execute") as mock_extract,
            patch.object(pipeline.convert_stage, "execute") as mock_convert,
            patch.object(pipeline.llm_stage, "execute") as mock_llm,
            patch.object(pipeline.save_stage, "execute") as mock_save,
            patch.object(
                pipeline.procurement_request_stage, "execute"
            ) as mock_procurement,
            patch("worker.pipeline.update_task_status") as mock_update_status,
            patch("worker.pipeline.extract_summary_text") as mock_extract_summary,
        ):
            mock_download.return_value = None
            mock_extract.return_value = None
            mock_convert.return_value = None
            mock_llm.return_value = None
            mock_save.return_value = None
            mock_procurement.return_value = None
            mock_extract_summary.return_value = ""

            context = PipelineContext("test-id")
            context.archive_path = "/tmp/archive.zip"
            context.extraction_result = {"result": "data"}
            context.content_length = 10000  # Small content

            result = await pipeline.execute("test-id")

            assert mock_download.called
            assert mock_extract.called
            assert mock_convert.called
            assert mock_llm.called
            assert mock_save.called
            assert mock_update_status.called

    @pytest.mark.asyncio
    async def test_pipeline_execute_rag_for_large_content(self):
        pipeline = ExtractionPipeline()

        # Mock stages to avoid real execution and control content_length
        with (
            patch.object(
                pipeline.download_stage, "execute", new_callable=AsyncMock
            ) as mock_download,
            patch.object(
                pipeline.extract_stage, "execute", new_callable=AsyncMock
            ) as mock_extract,
            patch.object(
                pipeline.convert_stage, "execute", new_callable=AsyncMock
            ) as mock_convert,
            patch.object(
                pipeline.llm_stage, "execute", new_callable=AsyncMock
            ) as mock_llm,
            patch.object(
                pipeline.save_stage, "execute", new_callable=AsyncMock
            ) as mock_save,
            patch(
                "worker.pipeline.RAGExtractionStage", spec=RAGExtractionStage
            ) as mock_rag_class,
            patch(
                "worker.pipeline.update_task_status", new_callable=AsyncMock
            ) as mock_update_status,
            patch(
                "worker.pipeline.extract_summary_text", return_value=""
            ) as mock_extract_summary,
        ):
            # Configure mocks
            mock_download.return_value = None
            mock_extract.return_value = None

            # Set content_length in convert_stage mock
            async def set_content_length(context, *args, **kwargs):
                context.content_length = 60000  # Large content

            mock_convert.side_effect = set_content_length

            mock_rag_stage = MagicMock()
            mock_rag_stage.execute = AsyncMock()
            mock_rag_class.return_value = mock_rag_stage

            mock_save.return_value = None

            result = await pipeline.execute("test-id")

            assert mock_download.called
            assert mock_extract.called
            assert mock_convert.called
            assert mock_rag_stage.execute.called
            assert not mock_llm.called  # Standard LLM should NOT be called
            assert mock_save.called
            assert mock_update_status.called


class TestProcurementRequestStage:
    @pytest.mark.asyncio
    async def test_procurement_stage_triggered_when_items_exist(self):
        pipeline = ExtractionPipeline()

        async def mock_llm_with_items(context, model=None):
            context.extraction_result = {
                "result": "data",
                "procurement_items": [{"name": "Item 1", "qty": 10}],
            }

        with (
            patch.object(pipeline.download_stage, "execute") as mock_download,
            patch.object(pipeline.extract_stage, "execute") as mock_extract,
            patch.object(pipeline.convert_stage, "execute") as mock_convert,
            patch.object(
                pipeline.llm_stage, "execute", side_effect=mock_llm_with_items
            ) as mock_llm,
            patch.object(pipeline.save_stage, "execute") as mock_save,
            patch.object(
                pipeline.procurement_request_stage, "execute"
            ) as mock_procurement,
            patch("worker.pipeline.update_task_status") as mock_update_status,
            patch("worker.pipeline.extract_summary_text") as mock_extract_summary,
        ):
            mock_download.return_value = None
            mock_extract.return_value = None
            mock_convert.return_value = None
            mock_save.return_value = None
            mock_procurement.return_value = None
            mock_extract_summary.return_value = ""

            result = await pipeline.execute("test-id")

            assert mock_procurement.called

    @pytest.mark.asyncio
    async def test_procurement_stage_not_triggered_when_empty_items(self):
        pipeline = ExtractionPipeline()

        with (
            patch.object(pipeline.download_stage, "execute") as mock_download,
            patch.object(pipeline.extract_stage, "execute") as mock_extract,
            patch.object(pipeline.convert_stage, "execute") as mock_convert,
            patch.object(pipeline.llm_stage, "execute") as mock_llm,
            patch.object(pipeline.save_stage, "execute") as mock_save,
            patch.object(
                pipeline.procurement_request_stage, "execute"
            ) as mock_procurement,
            patch("worker.pipeline.update_task_status") as mock_update_status,
            patch("worker.pipeline.extract_summary_text") as mock_extract_summary,
        ):
            mock_download.return_value = None
            mock_extract.return_value = None
            mock_convert.return_value = None
            mock_llm.return_value = None
            mock_save.return_value = None
            mock_procurement.return_value = None
            mock_extract_summary.return_value = ""

            context = PipelineContext("test-id")
            context.archive_path = "/tmp/archive.zip"
            context.extraction_result = {
                "result": "data",
                "procurement_items": [],
            }

            result = await pipeline.execute("test-id")

            assert not mock_procurement.called

    @pytest.mark.asyncio
    async def test_procurement_stage_not_triggered_when_no_procurement_items_field(
        self,
    ):
        pipeline = ExtractionPipeline()

        with (
            patch.object(pipeline.download_stage, "execute") as mock_download,
            patch.object(pipeline.extract_stage, "execute") as mock_extract,
            patch.object(pipeline.convert_stage, "execute") as mock_convert,
            patch.object(pipeline.llm_stage, "execute") as mock_llm,
            patch.object(pipeline.save_stage, "execute") as mock_save,
            patch.object(
                pipeline.procurement_request_stage, "execute"
            ) as mock_procurement,
            patch("worker.pipeline.update_task_status") as mock_update_status,
            patch("worker.pipeline.extract_summary_text") as mock_extract_summary,
        ):
            mock_download.return_value = None
            mock_extract.return_value = None
            mock_convert.return_value = None
            mock_llm.return_value = None
            mock_save.return_value = None
            mock_procurement.return_value = None
            mock_extract_summary.return_value = ""

            context = PipelineContext("test-id")
            context.archive_path = "/tmp/archive.zip"
            context.extraction_result = {"result": "data"}

            result = await pipeline.execute("test-id")

            assert not mock_procurement.called


def create_mock_stage(name, mock_method):
    stage = MagicMock()
    stage.__class__.__name__ = f"{name.capitalize()}Stage"
    stage.execute = mock_method
    return stage
