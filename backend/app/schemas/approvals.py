from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApprovalDecision(BaseModel):
    decision: str
    reviewer: str
    comment: str | None = None


class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    status: str
    reviewer: str | None
    comment: str | None
    created_at: datetime
    decided_at: datetime | None
