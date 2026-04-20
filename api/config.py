import logging
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tenders"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/tenders"

    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    openai_api_key: str = ""
    openai_base_url: str = "api.agentplatform.ru"
    openai_model: str = "openai/gpt-5.2-chat"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_public_url: str = "localhost:9000"

    worker_concurrency: int = 4

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

LOG_DIR = os.getenv("LOG_DIR", "/app/logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(),
        ],
    )
