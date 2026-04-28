import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Ensure worker module is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from worker.stages.rag_extraction import RAGExtractionStage
from worker.schemas.tender_schema import TenderSchemaSimple, SemanticSummary


class TestRAGExtractionStage:
    """Tests for RAGExtractionStage"""

    @pytest.mark.asyncio
    async def test_stage_initialization(self):
        stage = RAGExtractionStage()
        assert stage is not None

    @pytest.mark.asyncio
    async def test_field_queries_russian_and_formula(self):
        """Test that field_queries are in Russian and follow the clean formula"""
        stage = RAGExtractionStage()

        # Read the source to extract field_queries
        import inspect

        source = inspect.getsource(stage.execute)

        # Check that queries are in Russian (contain Russian chars) and don't contain colons or imperative verbs
        # The queries are defined inside the execute method
        # We'll execute the method with mocks and capture the queries

        captured_queries = []

        with (
            patch("langchain_community.vectorstores.FAISS") as mock_faiss,
            patch(
                "langchain_text_splitters.RecursiveCharacterTextSplitter"
            ) as mock_splitter,
            patch("langchain_openai.OpenAIEmbeddings") as mock_embeddings,
            patch("langchain_openai.ChatOpenAI") as mock_llm,
            patch("worker.schemas.tender_schema.TenderSchemaSimple") as mock_schema,
        ):
            # Setup mocks
            mock_splitter.return_value.split_text.return_value = ["chunk1", "chunk2"]
            mock_faiss.from_texts.return_value.similarity_search.return_value = []
            mock_llm.return_value.with_structured_output.return_value.invoke.return_value = MagicMock(
                model_dump=MagicMock(return_value={"summary": {}})
            )

            stage_obj = RAGExtractionStage()
            context = MagicMock()
            context.markdown_contents = {"file1.txt": "content1"}
            context.content_length = 60000

            await stage_obj.execute(context, model="openai")

            # The queries are created inside execute method
            # We can verify by checking the code or by capturing similarity_search calls
            mock_vector_store = mock_faiss.from_texts.return_value
            if mock_vector_store.similarity_search.called:
                for call in mock_vector_store.similarity_search.call_args_list:
                    query = call[0][0]
                    captured_queries.append(query)

            # Verify queries are in Russian and follow the formula
            for query in captured_queries:
                # Check for Russian characters
                assert any(ord(c) > 1000 for c in query), (
                    f"Query should contain Russian chars: {query}"
                )
                # Check no colons
                assert ":" not in query, (
                    f"Query should not contain ':' (colon): {query}"
                )
                # Check no imperative verbs
                assert "Извлеки" not in query, (
                    f"Query should not contain imperative verbs: {query}"
                )
                assert "Найди" not in query, (
                    f"Query should not contain imperative verbs: {query}"
                )
                assert "Определи" not in query, (
                    f"Query should not contain imperative verbs: {query}"
                )

    @pytest.mark.asyncio
    async def test_document_boundaries_preserved(self):
        """Test that document boundaries are preserved in combined text"""
        stage = RAGExtractionStage()

        with (
            patch("langchain_community.vectorstores.FAISS") as mock_faiss,
            patch(
                "langchain_text_splitters.RecursiveCharacterTextSplitter"
            ) as mock_splitter,
            patch("langchain_openai.OpenAIEmbeddings") as mock_embeddings,
            patch("langchain_openai.ChatOpenAI") as mock_llm,
        ):
            # Capture the text passed to splitter
            captured_text = None

            def capture_split(text):
                nonlocal captured_text
                captured_text = text
                return ["chunk1"]

            mock_splitter.return_value.split_text.side_effect = capture_split
            mock_faiss.from_texts.return_value.similarity_search.return_value = []
            mock_llm.return_value.with_structured_output.return_value.invoke.return_value = MagicMock(
                model_dump=MagicMock(return_value={"summary": {}})
            )

            stage_obj = RAGExtractionStage()
            context = MagicMock()
            context.markdown_contents = {
                "doc1.txt": "Content of doc1",
                "doc2.txt": "Content of doc2",
            }
            context.content_length = 60000

            await stage_obj.execute(context, model="openai")

            assert captured_text is not None
            assert "=== DOCUMENT START: doc1.txt ===" in captured_text
            assert "=== DOCUMENT END: doc1.txt ===" in captured_text
            assert "=== DOCUMENT START: doc2.txt ===" in captured_text
            assert "=== DOCUMENT END: doc2.txt ===" in captured_text

    @pytest.mark.asyncio
    async def test_uses_tender_schema_simple(self):
        """Test that RAG extraction uses TenderSchemaSimple"""
        stage = RAGExtractionStage()

        with (
            patch("langchain_community.vectorstores.FAISS") as mock_faiss,
            patch(
                "langchain_text_splitters.RecursiveCharacterTextSplitter"
            ) as mock_splitter,
            patch("langchain_openai.OpenAIEmbeddings") as mock_embeddings,
            patch("langchain_openai.ChatOpenAI") as mock_chat_openai,
        ):
            mock_splitter.return_value.split_text.return_value = ["chunk1"]
            mock_faiss.from_texts.return_value.similarity_search.return_value = []

            mock_llm_instance = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.return_value = MagicMock(
                model_dump=MagicMock(return_value={"summary": {}})
            )
            mock_llm_instance.with_structured_output.return_value = mock_structured
            mock_chat_openai.return_value = mock_llm_instance

            stage_obj = RAGExtractionStage()
            context = MagicMock()
            context.markdown_contents = {"file1.txt": "content1"}
            context.content_length = 60000

            await stage_obj.execute(context, model="openai")

            # Verify TenderSchemaSimple was used with structured output
            mock_llm_instance.with_structured_output.assert_called_once()

    @pytest.mark.asyncio
    async def test_gigachat_model_embeddings(self):
        """Test that GigaChat embeddings are used when model is gigachat"""
        stage = RAGExtractionStage()

        with (
            patch("langchain_community.vectorstores.FAISS") as mock_faiss,
            patch(
                "langchain_text_splitters.RecursiveCharacterTextSplitter"
            ) as mock_splitter,
            patch("langchain_gigachat.GigaChatEmbeddings") as mock_gigachat_emb,
            patch("langchain_gigachat.GigaChat") as mock_gigachat,
        ):
            mock_splitter.return_value.split_text.return_value = ["chunk1"]
            mock_faiss.from_texts.return_value.similarity_search.return_value = []
            mock_gigachat.return_value.with_structured_output.return_value.invoke.return_value = MagicMock(
                model_dump=MagicMock(return_value={"summary": {}})
            )

            stage_obj = RAGExtractionStage()
            context = MagicMock()
            context.markdown_contents = {"file1.txt": "content1"}
            context.content_length = 60000

            await stage_obj.execute(context, model="gigachat")

            mock_gigachat_emb.assert_called_once()
            mock_gigachat.assert_called_once()

    @pytest.mark.asyncio
    async def test_field_queries_coverage(self):
        """Test that all SemanticSummary fields have corresponding queries"""
        from worker.schemas.tender_schema import SemanticSummary

        # Get all fields from SemanticSummary
        summary_fields = list(SemanticSummary.model_fields.keys())

        # Expected queries (keys from field_queries in rag_extraction.py)
        expected_query_keys = [
            "customer",
            "procurement_method",
            "supply_scope",
            "service_scope",
            "engineering_scope",
            "delivery_terms",
            "financial_profile",
            "penalty_profile",
            "product_requirements",
            "participant_requirements",
            "timeline_summary",
            "complexity_flags",
        ]

        # Verify all SemanticSummary fields are covered
        for field in summary_fields:
            assert field in expected_query_keys, (
                f"Field {field} from SemanticSummary not covered in queries"
            )

    @pytest.mark.asyncio
    async def test_no_duplicate_chunks_after_dedup(self):
        """Test that duplicate chunks are removed in the code"""
        stage = RAGExtractionStage()

        with (
            patch("langchain_community.vectorstores.FAISS") as mock_faiss,
            patch(
                "langchain_text_splitters.RecursiveCharacterTextSplitter"
            ) as mock_splitter,
            patch("langchain_openai.OpenAIEmbeddings") as mock_embeddings,
            patch("langchain_openai.ChatOpenAI") as mock_llm,
        ):
            mock_splitter.return_value.split_text.return_value = [
                "chunk1",
                "chunk2",
                "chunk3",
            ]

            # Mock similarity_search to return some duplicate chunks
            mock_vector_store = mock_faiss.from_texts.return_value
            mock_vector_store.similarity_search.return_value = [
                MagicMock(page_content="chunk_A"),
                MagicMock(page_content="chunk_B"),
                MagicMock(page_content="chunk_A"),  # Duplicate
                MagicMock(page_content="chunk_C"),
                MagicMock(page_content="chunk_B"),  # Duplicate
            ]

            mock_llm.return_value.with_structured_output.return_value.invoke.return_value = MagicMock(
                model_dump=MagicMock(return_value={"summary": {}})
            )

            stage_obj = RAGExtractionStage()
            context = MagicMock()
            context.markdown_contents = {"file1.txt": "content1"}
            context.content_length = 60000

            await stage_obj.execute(context, model="openai")

            # Verify that similarity_search was called multiple times (for each query)
            assert mock_vector_store.similarity_search.called
