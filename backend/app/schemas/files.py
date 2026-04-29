from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DocumentFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    content_type: str | None
    size_bytes: int
    checksum_sha256: str
    storage_key: str
    status: str
    parser_name: str | None
    parse_warnings: list[dict[str, Any]]
    metadata_json: dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime
