from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class ExtractionCreate(BaseModel):
    archive_url: str = Field(description="URL to download the archive")
    tender_id: str = Field(description="Tender identifier")
    model: Literal["openai", "gigachat"] = Field(
        default="openai",
        description="LLM model to use for extraction: 'openai' or 'gigachat'",
    )


class ExtractionResponse(BaseModel):
    id: str
    tender_id: str
    archive_url: str
    model: str = "openai"
    status: str
    current_stage: Optional[str] = None
    stage_progress: Optional[dict] = None
    result_json: Optional[dict] = None
    failed_files: Optional[list] = None
    summary_text: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExtractionStatusResponse(BaseModel):
    task_id: str
    status: str
    current_stage: Optional[str] = None
    result_json: Optional[dict] = None
    failed_files: Optional[list] = None
    summary_text: Optional[str] = None
    procurement_request_url: Optional[str] = None
    error_message: Optional[str] = None
