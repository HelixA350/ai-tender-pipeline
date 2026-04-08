CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS extraction_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tender_id VARCHAR(255) NOT NULL,
    archive_url TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    current_stage VARCHAR(30),
    stage_progress JSONB DEFAULT '{}',
    result_json JSONB,
    failed_files JSONB DEFAULT '[]',
    summary_text TEXT,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON extraction_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_tender_id ON extraction_tasks(tender_id);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON extraction_tasks(created_at);
