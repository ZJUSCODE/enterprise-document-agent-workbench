from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.approvals import ApprovalOut


class TaskCreate(BaseModel):
    file_id: str
    template_id: str = "contract_review"
    task_type: str = "document_extract"
    priority: int = Field(default=5, ge=1, le=9)
    submitted_by: str = "system"


class BatchTaskCreate(BaseModel):
    file_ids: list[str]
    template_id: str = "contract_review"
    task_type: str = "document_extract"
    priority: int = Field(default=5, ge=1, le=9)
    submitted_by: str = "system"


class TaskRevision(BaseModel):
    extracted_fields: dict[str, Any] | None = None
    summary: dict[str, Any] | None = None
    anomalies: list[dict[str, Any]] | None = None
    revised_by: str = "reviewer"
    comment: str | None = None


class TaskEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    status: str
    progress: int
    level: str
    message: str
    created_at: datetime


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_id: str
    template_id: str
    task_type: str
    status: str
    progress: int
    retry_count: int
    max_retries: int
    priority: int
    submitted_by: str
    classified_as: str | None
    extracted_fields: dict[str, Any]
    table_data: list[dict[str, Any]]
    summary: dict[str, Any]
    anomalies: list[dict[str, Any]]
    generated_artifact_key: str | None
    error_message: str | None
    result_version: int
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class TaskDetailOut(TaskOut):
    events: list[TaskEventOut] = []
    approvals: list[ApprovalOut] = []


class ResultVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    version: int
    artifact_key: str | None
    extracted_fields: dict[str, Any]
    summary: dict[str, Any]
    anomalies: list[dict[str, Any]]
    created_by: str
    created_at: datetime
