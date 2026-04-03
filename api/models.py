from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class ExtractionCreate(BaseModel):
    archive_url: str = Field(description="URL to download the archive")
    tender_id: str = Field(description="Tender identifier")


class ExtractionResponse(BaseModel):
    id: UUID
    tender_id: str
    archive_url: str
    status: str
    current_stage: Optional[str] = None
    stage_progress: Optional[dict] = None
    result_json: Optional[dict] = None
    failed_files: Optional[list] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExtractionStatusResponse(BaseModel):
    task_id: UUID
    status: str
    current_stage: Optional[str] = None
    result_json: Optional[dict] = None
    failed_files: Optional[list] = None
    error_message: Optional[str] = None
