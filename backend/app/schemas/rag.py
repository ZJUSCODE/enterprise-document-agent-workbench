from typing import Any

from pydantic import BaseModel, Field


class RagQuery(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_type: str | None = None
    file_id: str | None = None


class RagHitOut(BaseModel):
    chunk_id: str
    file_id: str
    task_id: str | None
    document_type: str | None
    score: float
    text: str
    metadata: dict[str, Any]


class RagAnswerOut(BaseModel):
    question: str
    answer: str
    hits: list[RagHitOut]


class RagReindexOut(BaseModel):
    indexed_tasks: int
    indexed_chunks: int
