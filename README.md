# AI Tender Pipeline

Backend для извлечения структурированных данных из тендерной документации с использованием AI.

## Стек

- **FastAPI** — REST API
- **RabbitMQ** — Message queue
- **Celery** — Task queue worker
- **PostgreSQL** — База данных
- **LangChain + OpenAI** — LLM для извлечения данных
- **markitdown** — Конвертация файлов в Markdown
- **Docker + Docker Compose** — Контейнеризация

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Копирование .env
cp .env.example .env

# Редактирование .env (настройка OpenAI)
nano .env
```

### 2. Запуск

```bash
docker-compose up -d
```

### 3. Проверка

```bash
# Health check
curl http://localhost:8000/health/

# API документация
open http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenders/extraction` | Создать задачу на извлечение |
| GET | `/tenders/extraction/{task_id}` | Получить статус/результат |
| GET | `/health/` | Health check |

### Пример использования

```bash
# Создание задачи
curl -X POST http://localhost:8000/tenders/extraction \
  -H "Content-Type: application/json" \
  -d '{
    "archive_url": "https://example.com/tender.zip",
    "tender_id": "TENDER-2024-001"
  }'

# Ответ
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tender_id": "TENDER-2024-001",
  "archive_url": "https://example.com/tender.zip",
  "status": "pending",
  ...
}

# Проверка статуса
curl http://localhost:8000/tenders/extraction/550e8400-e29b-41d4-a716-446655440000

# Ответ (в процессе)
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "current_stage": "llm",
  ...
}

# Ответ (завершено)
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result_json": {
    "tender_id": "...",
    "identification": {...},
    ...
  }
}
```

## Архитектура

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  FastAPI (API)                          │
│  - POST /tenders/extraction → RabbitMQ   │
│  - GET /tenders/extraction/{id} → PG    │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│  RabbitMQ (queue: tender_tasks)          │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│  Celery Worker                          │
│  Pipeline Stages:                       │
│  1. Download → 2. Extract → 3. Convert  │
│  4. LLM → 5. Save (background)          │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│  PostgreSQL                             │
└─────────────────────────────────────────┘
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | PostgreSQL async URL | postgresql+asyncpg://... |
| `DATABASE_URL_SYNC` | PostgreSQL sync URL | postgresql://... |
| `RABBITMQ_URL` | RabbitMQ URL | amqp://guest:guest@localhost:5672/ |
| `OPENAI_API_KEY` | API ключ OpenAI | - |
| `OPENAI_BASE_URL` | Base URL API | api.agentplatform.ru |
| `OPENAI_MODEL` | Модель | openai/gpt-5.2-chat |

## Расширение pipeline

Для добавления новых этапов обработки:

1. Создайте новый файл в `worker/stages/`
2. Реализуйте класс с методом `async def execute(self, context)`
3. Добавьте в список `self.stages` в `worker/pipeline.py`

```python
# worker/stages/my_new_stage.py
class MyNewStage:
    async def execute(self, context):
        # Ваша логика
        context.some_data = "processed"
```

## Тестирование

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest tests/ -v
```

## Лицензия

MIT
