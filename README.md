# AI Tender Pipeline

Backend для извлечения структурированных данных из тендерной документации с использованием AI.

## Стек

- **FastAPI** — REST API
- **Kafka** — Message queue
- **PostgreSQL** — База данных
- **LangChain + OpenAI/GigaChat** — LLM для извлечения данных
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
| POST | `/poll` | Poll/callback endpoint |

---

## Форматы данных

### POST /tenders/extraction

Создание задачи на извлечение данных из архива тендерной документации.

**Request:**
```json
{
  "archive_url": "https://example.com/tender.zip",
  "tender_id": "TENDER-2024-001"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `archive_url` | string | Да | URL для скачивания архива (zip, rar, 7z, tar.gz) |
| `tender_id` | string | Да | Идентификатор тендера, для связи с CRM |

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tender_id": "TENDER-2024-001",
  "archive_url": "https://example.com/tender.zip",
  "status": "pending",
  "current_stage": null,
  "stage_progress": {},
  "result_json": null,
  "failed_files": null,
  "summary_text": null,
  "error_message": null,
  "retry_count": 0,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### GET /tenders/extraction/{task_id}

Получение статуса и результата обработки.

**Response (в процессе):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "current_stage": "llm",
  "result_json": null,
  "failed_files": null,
  "summary_text": null,
  "error_message": null
}
```

**Response (завершено):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "current_stage": "completed",
  "result_json": {
    "tender_id": "550e8400-e29b-41d4-a716-446655440000",
    "summary_text": "Заказчик: ООО РН-НПЗ | Способ закупки: Запрос предложений | Номенклатура: Фильтры для компрессоров | ...",
    "error_message": "",
    "status": "completed",
    "table_tender": {
      "procurement_items": [
        {
          "no": 1,
          "request_number": null,
          "article": "123456",
          "name": "Фильтр",
          "qty": 10,
          "unit": "ШТ",
          "brand": null,
          "manufacturer": "Example",
          "equipment_model": null,
          "serial_number": null,
          "drawing": null,
          "drawing_position": null,
          "material": null,
          "comments": null
        }
      ]
    }
  },
  "failed_files": ["document.pdf"],
  "summary_text": "Заказчик: ООО РН-НПЗ | Способ закупки: Запрос предложений | Номенклатура: Фильтры для компрессоров | ...",
  "procurement_request_url": null,
  "error_message": null
}
```

---

### Ответы status

| Status | Описание |
|--------|-----------|
| `pending` | Задача создана, в очереди |
| `processing` | Задача в обработке |
| `completed` | Успешно завершено |
| `failed` | Ошибка при обработке |

---

## Архитектура

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  FastAPI (API)                          │
│  - POST /tenders/extraction → Kafka     │
│  - GET /tenders/extraction/{id} → PG    │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│  Kafka (topic: extraction-tasks)         │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│  Worker                                 │
│  Pipeline Stages:                       │
│  1. Download → 2. Extract → 3. Convert  │
│  4. LLM (TenderSchemaShort)             │
│  5. Save (background)                   │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│  PostgreSQL                             │
└─────────────────────────────────────────┘
```

### Этапы Pipeline

1. **Download** — Скачивание архива по URL
2. **Extract** — Извлечение файлов из архива (zip, rar, 7z, tar.gz)
3. **Convert** — Конвертация файлов в Markdown (markitdown)
4. **LLM** — Извлечение структурированных данных через LangChain + OpenAI/GigaChat с использованием `TenderSchemaShort`
5. **Save** — Сохранение результата в БД (фоновая задача)

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | PostgreSQL async URL | postgresql+asyncpg://postgres:postgres@postgres:5432/tenders |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka bootstrap servers | localhost:9092 |
| `OPENAI_API_KEY` | API ключ OpenAI | - |
| `OPENAI_BASE_URL` | Base URL API | api.agentplatform.ru |
| `OPENAI_MODEL` | Модель OpenAI | gpt-4o |
| `GIGACHAT_API_KEY` | API ключ GigaChat | - |
| `GIGACHAT_MODEL` | Модель GigaChat | GigaChat-Pro |

---

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

---

## Тестирование

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest tests/ -v
```

---

## Мониторинг

```bash
# Логи API
docker-compose logs -f api

# Логи Worker
docker-compose logs -f worker
```
