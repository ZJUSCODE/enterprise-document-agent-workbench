from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.models import TemplateDefinition
from app.services.template_registry import BUILTIN_TEMPLATES


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_builtin_templates(db: Session) -> None:
    for template in BUILTIN_TEMPLATES:
        existing = db.get(TemplateDefinition, template["id"])
        if existing:
            continue
        db.add(TemplateDefinition(**template))
    db.commit()
