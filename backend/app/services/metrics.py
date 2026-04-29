from collections import Counter
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Approval, WorkflowTask
from app.schemas.metrics import EvaluationSummary


SUCCESS_STATUSES = {"approved", "completed", "waiting_approval"}


def evaluation_summary(db: Session) -> EvaluationSummary:
    tasks = list(db.scalars(select(WorkflowTask)).all())
    total = len(tasks)
    status_breakdown = Counter(task.status for task in tasks)
    anomaly_counter: Counter[str] = Counter()
    durations = []
    quality_scores = []
    for task in tasks:
        for anomaly in task.anomalies or []:
            anomaly_counter[anomaly.get("code", "unknown")] += 1
        if task.started_at and task.completed_at:
            durations.append(_seconds_between(task.started_at, task.completed_at))
        quality = (task.summary or {}).get("quality_score")
        if isinstance(quality, (int, float)):
            quality_scores.append(float(quality))

    approval_count = db.scalar(select(func.count()).select_from(Approval)) or 0
    manual_takeover_count = sum(1 for task in tasks if task.status in {"rejected", "needs_revision", "failed"} or task.anomalies)
    success_count = sum(1 for task in tasks if task.status in SUCCESS_STATUSES)

    return EvaluationSummary(
        total_tasks=total,
        success_rate=_ratio(success_count, total),
        approval_rate=_ratio(approval_count, total),
        manual_takeover_rate=_ratio(manual_takeover_count, total),
        average_duration_seconds=round(sum(durations) / len(durations), 3) if durations else 0.0,
        extraction_accuracy_proxy=round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else 0.0,
        status_breakdown=dict(status_breakdown),
        anomaly_breakdown=dict(anomaly_counter),
    )


def _seconds_between(start: datetime, end: datetime) -> float:
    return max(0.0, (end - start).total_seconds())


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 0.0
