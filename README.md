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
    "meta": {
      "source_files": ["doc1.pdf", "spec.xlsx"],
      "tender_types": ["закупка"],
      "package_comments": null
    },
    "tender_id": "TENDER-2024-001",
    "tender_types": ["закупка"],
    "summary": {
      "customer": "Нефтеперерабатывающий завод в Хабаровском крае (ПАО Роснефть)",
      "procurement_method": "Запрос предложений на SAP SRM, переторг разрешён",
      "supply_scope": "Поставка 34 позиций запасных частей для дизельного двигателя Caterpillar 3512",
      "service_scope": null,
      "engineering_scope": null,
      "delivery_terms": "DDP склад заказчика (г. Нефтеюганск), срок поставки — 90 дней",
      "financial_profile": "НМЦ 4,2 млн руб. с НДС 20%. Оплата по факту поставки в течение 30 дней",
      "penalty_profile": "0,1% за каждый день просрочки, максимум 10%",
      "product_requirements": "Только новое оборудование. Гарантия 24 месяца",
      "participant_requirements": null,
      "timeline_summary": "Заявки до 15 мая 2025 (МСК), поставка 60 дней",
      "complexity_flags": "Удалённый регион; жёсткая привязка к бренду"
    },
    "identification": {
      "tender_id": "РН60306304",
      "external_id": null,
      "source": null
    },
    "general": {
      "name": "Фильтры, корпуса, сальники...",
      "method": "Запрос (Т)КП",
      "status": "Приём заявок",
      "platform": "ТЭК-Торг",
      "platform_url": null,
      "lot_divisible": null,
      "rebidding_allowed": null,
      "notes": null
    },
    "parties": {
      "customer": {
        "name": "ООО \"РН-КОМСОМОЛЬСКИЙ НПЗ\"",
        "full_name": null,
        "inn": "27030328...",
        "kpp": null,
        "address": null,
        "contact_persons": null,
        "procurement_org": null,
        "procurement_group": null,
        "notes": null
      },
      "notes": null
    },
    "dates": {
      "publication_date": "2026-03-30",
      "submission_deadline": "2026-04-10",
      "submission_time": "09:00:00",
      "submission_timezone": "МСК+3",
      "opening_date": null,
      "opening_time": null,
      "results_date": null,
      "clarification_request_deadline": null,
      "delivery_start": null,
      "delivery_end": null,
      "early_delivery_allowed": null,
      "notes": null
    },
    "financials": {
      "nmck": null,
      "bid_security": null,
      "contract_security": null,
      "auction_step": null,
      "currencies": null,
      "base_currency": null,
      "vat_rate": null,
      "prices_include_vat": null,
      "payment_terms": null,
      "incoterms": null,
      "penalties": null,
      "notes": null
    },
    "procurement_items": [
      {
        "position": 1,
        "name": "Фильтр",
        "article": "123456",
        "manufacturer": "Example",
        "qty": 10,
        "unit": "шт",
        "npp": null,
        "category": null,
        "unit_price": null,
        "currency": null,
        "delivery_date": null,
        "delivery_location": null,
        "analog_allowed": null,
        "original_reference": null,
        "linked_service": null,
        "source": null,
        "notes": null
      }
    ],
    "special_items": null,
    "items_summary": {
      "total_positions": 1,
      "total_qty_units": 10,
      "price_filled": false,
      "manufacturers_unique": null,
      "is_single_manufacturer": null
    },
    "product_requirements": {
      "condition": "новый",
      "warranty_months": null,
      "warranty_start": null,
      "analog_allowed": null,
      "analog_rules": null,
      "import_substitution_required": null,
      "import_substitution_registry": null,
      "origin_restrictions": null,
      "notes": null
    },
    "service_scope": null,
    "engineering_scope": null,
    "participant_requirements": null,
    "submission_documents": null,
    "scoring_signals": null
  },
  "failed_files": ["document.pdf"],
  "summary_text": "Заказчик: ООО РН-НПЗ | Способ закупки: Запрос предложений | Номенклатура: Фильтры для компрессоров | ...",
  "procurement_request_url": "http://minio.example.com/550e8400-e29b-41d4-a716-446655440000/zakupka.xlsx",
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
│  - POST /tenders/extraction → RabbitMQ   │
│  - GET /tenders/extraction/{id} → PG    │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│  RabbitMQ (queue: celery)               │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│  Celery Worker                          │
│  Pipeline Stages:                       │
│  1. Download → 2. Extract → 3. Convert  │
│  4. LLM (with_structured_output)        │
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
4. **LLM** — Извлечение структурированных данных через LangChain + OpenAI с использованием `with_structured_output()`
5. **Zakupka** — Создание Excel-заявки для отдела закупок (сохранение в Minio)
6. **Save** — Сохранение результата в БД (фоновая задача)

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | PostgreSQL async URL | postgresql+asyncpg://postgres:postgres@postgres:5432/tenders |
| `DATABASE_URL_SYNC` | PostgreSQL sync URL | postgresql://postgres:postgres@postgres:5432/tenders |
| `RABBITMQ_URL` | RabbitMQ URL | amqp://guest:guest@rabbitmq:5672/ |
| `OPENAI_API_KEY` | API ключ OpenAI | - |
| `OPENAI_BASE_URL` | Base URL API | api.agentplatform.ru |
| `OPENAI_MODEL` | Модель | openai/gpt-5.2-chat |
| `MINIO_PUBLIC_URL` | Публичный URL Minio | - |

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
