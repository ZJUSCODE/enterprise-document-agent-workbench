from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.metrics import EvaluationSummary
from app.services.metrics import evaluation_summary

router = APIRouter()


@router.get("/evaluation", response_model=EvaluationSummary)
def get_evaluation_summary(db: Session = Depends(get_db)) -> EvaluationSummary:
    return evaluation_summary(db)
