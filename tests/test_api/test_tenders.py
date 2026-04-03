import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from api.main import app


@pytest.fixture
def mock_db_session():
    with patch("api.routers.tenders.get_db") as mock:
        mock_session = AsyncMock()
        mock.return_value = mock_session
        yield mock_session


@pytest.fixture
def mock_celery_task():
    with patch("api.routers.tenders.celery_app.send_task") as mock:
        mock.return_value = MagicMock(id="test-task-id")
        yield mock


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_create_extraction_task():
    transport = ASGITransport(app=app)

    with (
        patch("api.routers.tenders.get_db") as mock_db,
        patch("api.routers.tenders.celery_app.send_task") as mock_task,
    ):
        mock_session = AsyncMock()
        mock_db.return_value = mock_session
        mock_task.return_value = MagicMock(id="test-task-id")

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        task_mock = MagicMock()
        task_mock.id = "test-uuid"
        task_mock.tender_id = "TENDER-001"
        task_mock.archive_url = "https://example.com/archive.zip"
        task_mock.status = "pending"
        task_mock.stage_progress = {}
        task_mock.created_at = "2024-01-01T00:00:00"
        task_mock.updated_at = "2024-01-01T00:00:00"
        mock_session.refresh = lambda x: setattr(x, "__dict__", task_mock.__dict__)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/tenders/extraction",
                json={
                    "archive_url": "https://example.com/archive.zip",
                    "tender_id": "TENDER-001",
                },
            )

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_extraction_status_not_found():
    transport = ASGITransport(app=app)

    with patch("api.routers.tenders.get_db") as mock_db:
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = lambda: None
        mock_session.execute = AsyncMock(return_value=mock_result)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/tenders/extraction/550e8400-e29b-41d4-a716-446655440000"
            )

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_get_extraction_status_completed():
    transport = ASGITransport(app=app)

    with patch("api.routers.tenders.get_db") as mock_db:
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        task = MagicMock()
        task.id = "550e8400-e29b-41d4-a716-446655440000"
        task.status = "completed"
        task.current_stage = "save"
        task.result_json = {"tender_id": "TENDER-001"}
        task.error_message = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = lambda: task
        mock_session.execute = AsyncMock(return_value=mock_result)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/tenders/extraction/550e8400-e29b-41d4-a716-446655440000"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result_json"] == {"tender_id": "TENDER-001"}
