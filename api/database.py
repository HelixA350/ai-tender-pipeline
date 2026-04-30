from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from datetime import datetime
import os

from api.config import settings

DB_PATH = settings.database_url.replace("sqlite+aiosqlite:///", "")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class ExtractionTask(Base):
    __tablename__ = "extraction_tasks"

    id = Column(String(36), primary_key=True)
    tender_id = Column(Integer, nullable=False, index=True)
    archive_url = Column(Text, nullable=False)
    model = Column(String(20), default="chatgpt")
    status = Column(String(20), default="pending", index=True)
    current_stage = Column(String(30), nullable=True)
    stage_progress = Column(JSON, default=dict)
    result_json = Column(JSON, nullable=True)
    failed_files = Column(JSON, default=list)
    summary_text = Column(Text, nullable=True)
    procurement_request_url = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


async def get_db():
    async with async_session_maker() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
