from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TemplateDefinitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    document_type: str
    output_format: str
    body: str
    version: str
    created_at: datetime
    updated_at: datetime
