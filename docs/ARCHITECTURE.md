# Архитектура AI Tender Pipeline

## Обзор

AI Tender Pipeline — это система для автоматического извлечения структурированных данных из тендерной документации с использованием AI.

## Компоненты

### 1. API (FastAPI)

**Файл**: `api/main.py`

**Назначение**: REST API для управления задачами извлечения данных.

**Эндпоинты**:
- `POST /tenders/extraction` — создание задачи
- `GET /tenders/extraction/{task_id}` — получение статуса/результата
- `GET /health/` — health check

### 2. База данных (PostgreSQL)

**Файл**: `db/init.sql`, `api/database.py`

**Таблица**: `extraction_tasks`

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | UUID | Primary key |
| tender_id | VARCHAR(255) | ID тендера |
| archive_url | TEXT | URL архива |
| status | VARCHAR(20) | pending, processing, completed, failed |
| current_stage | VARCHAR(30) | Текущий этап |
| stage_progress | JSONB | Прогресс по этапам |
| result_json | JSONB | Результат извлечения |
| error_message | TEXT | Сообщение об ошибке |
| retry_count | INT | Количество попыток |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

### 3. Очередь задач (RabbitMQ + Celery)

**Файлы**: `worker/celery_app.py`, `worker/tasks.py`

**Назначение**: Асинхронная обработка задач извлечения данных.

**Очередь**: `tender_tasks`

**Поведение**:
- При создании задачи через API, задача отправляется в очередь
- Worker обрабатывает задачу асинхронно
- При ошибке задача автоматически перезапускается (max_retries=3)

### 4. Pipeline обработки

**Файл**: `worker/pipeline.py`

**Этапы обработки**:

```
[Скачивание] → [Извлечение из архива] → [Конвертация в Markdown] → [Извлечение LLM] → [Сохранение]
   ↓              ↓                    ↓                      ↓                  ↓
 Stage 1       Stage 2               Stage 3                Stage 4            Stage 5 (background)
```

#### Stage 1: Download
**Файл**: `worker/stages/download.py`

Скачивает архив по URL во временный файл.

#### Stage 2: Extract
**Файл**: `worker/stages/extract.py`

Извлекает файлы из архива (zip, tar.gz, 7z, rar).

#### Stage 3: Convert
**Файл**: `worker/stages/convert.py`

Конвертирует файлы в Markdown с помощью markitdown:
- PDF, DOCX, XLSX → Markdown
- URL → HTML → Markdown
- Изображения → описание через OpenAI (опционально)

#### Stage 4: Extract LLM
**Файл**: `worker/stages/extract_llm.py`

Извлекает структурированные данные с помощью OpenAI:
- Использует Pydantic schema (`worker/schemas/tender_schema.py`)
- `with_structured_output()` для гарантированного JSON

#### Stage 5: Save (Background)
**Файл**: `worker/stages/save.py`

Сохраняет результат в БД асинхронно:
- Non-blocking для клиента
- Retry логика (3 попытки)

## Паттерны и принципы

### 1. Stage-based Pipeline

Каждый этап — отдельный класс с методом `async def execute(self, context)`.

**Добавление нового этапа**:

```python
# worker/stages/my_stage.py
class MyStage:
    async def execute(self, context):
        # Логика этапа
        context.my_result = "value"

# worker/pipeline.py
self.stages = [
    DownloadStage(),
    ExtractStage(),
    ConvertStage(),
    MyStage(),  # <-- новый этап
    ExtractLLMStage(),
    SaveStage(),
]
```

### 2. Progress Tracking

После каждого этапа обновляется `stage_progress` в БД:

```json
{
  "download": true,
  "extract": true,
  "convert": true,
  "llm": false,
  "save": false
}
```

При повторном запуске (после ошибки/краша) worker продолжает с последнего успешного этапа.

### 3. Background DB Writes

Сохранение результата не блокирует ответ клиенту:

```python
async def execute(self, context):
    # Fire and forget
    asyncio.create_task(self._save_async(context))
```

### 4. Error Handling

- Каждый этап логирует прогресс
- При ошибке обновляется `status: failed` и `error_message`
- Celery автоматически перезапускает задачу (max_retries=3)

## Конфигурация

### OpenAI

Настраивается через переменные окружения:

```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=api.agentplatform.ru
OPENAI_MODEL=openai/gpt-5.2-chat
```

### Database

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tenders
```

### RabbitMQ

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
```

## Масштабирование

### Горизонтальное масштабирование

Для увеличения пропускной способности добавьте больше worker instances:

```yaml
# docker-compose.yml
worker:
  # ...
  deploy:
    replicas: 3
```

### Вертикальное масштабирование

Увеличение concurrency:

```bash
celery -A worker.celery_app worker --loglevel=info --concurrency=8
```

## Мониторинг

### Health Checks

- **API**: `GET /health/` → `{"status": "healthy"}`
- **PostgreSQL**: встроенный healthcheck в docker-compose
- **RabbitMQ**: встроенный healthcheck в docker-compose
- **Worker**: через Celery events (опционально)

### Логирование

Логи выводятся в stdout/stderr контейнеров.

```bash
# Просмотр логов API
docker-compose logs api

# Просмотр логов Worker
docker-compose logs worker

# Real-time логи
docker-compose logs -f worker
```

## Безопасность

### Аутентификация

На текущий момент не реализована. Для production:

1. Добавить API key authentication
2. Использовать HTTPS
3. Настроить VLAN/network isolation

### Secrets

- API keys хранятся в переменных окружения
- В production использовать Docker secrets или Vault

## Troubleshooting

### Задача зависла в "processing"

```bash
# Проверить статус в БД
docker-compose exec postgres psql -U postgres -d tenders -c "SELECT * FROM extraction_tasks WHERE status='processing';"

# Ручной перезапуск задачи
docker-compose exec worker celery -A worker.celery_app control revoke <task_id>
```

### Ошибка "Connection refused"

```bash
# Проверить запущенные сервисы
docker-compose ps

# Проверить connectivity
docker-compose exec api ping rabbitmq
docker-compose exec api ping postgres
```

### OOM (Out of Memory)

```bash
# Ограничить память
docker-compose up -d --scale worker=2 --memory=512m
```

## Future Enhancements

1. **增量提取** — инкрементальное извлечение при обновлении архива
2. **Webhooks** — уведомление о завершении через webhook
3. **Metrics** — Prometheus/Grafana метрики
4. **Rate limiting** — ограничение частоты запросов
5. **Authentication** — JWT/API key auth
