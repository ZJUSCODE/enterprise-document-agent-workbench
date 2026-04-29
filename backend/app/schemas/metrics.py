from pydantic import BaseModel


class EvaluationSummary(BaseModel):
    total_tasks: int
    success_rate: float
    approval_rate: float
    manual_takeover_rate: float
    average_duration_seconds: float
    extraction_accuracy_proxy: float
    status_breakdown: dict[str, int]
    anomaly_breakdown: dict[str, int]
