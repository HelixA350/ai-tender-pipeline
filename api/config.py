import logging
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:////app/db/tenders.db"
    database_url_sync: str = "sqlite:////app/db/tenders.db"

    kafka_bootstrap_servers: str = "localhost:9092"

    gigachat_api_key: str = ""
    gigachat_model: str = "GigaChat-2-Max"

    openai_api_key: str = ""
    openai_base_url: str = "api.agentplatform.ru"
    openai_model: str = "openai/gpt-5-chat-latest"

    worker_concurrency: int = 4
    webhook_url: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

LOG_DIR = os.getenv("LOG_DIR", "/app/logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(),
        ],
    )
