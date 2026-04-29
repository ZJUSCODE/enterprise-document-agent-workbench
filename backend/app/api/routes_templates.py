from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import TemplateDefinition
from app.schemas.templates import TemplateDefinitionOut

router = APIRouter()


@router.get("", response_model=list[TemplateDefinitionOut])
def list_templates(db: Session = Depends(get_db)) -> list[TemplateDefinition]:
    return list(db.scalars(select(TemplateDefinition).order_by(TemplateDefinition.name)).all())


@router.get("/{template_id}", response_model=TemplateDefinitionOut)
def get_template(template_id: str, db: Session = Depends(get_db)) -> TemplateDefinition:
    template = db.get(TemplateDefinition, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
