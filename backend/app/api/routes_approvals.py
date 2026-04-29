from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Approval, WorkflowTask
from app.schemas.approvals import ApprovalDecision, ApprovalOut
from app.core.security import Principal, get_current_principal, require_roles
from app.services.audit import record_audit
from app.services.workflow import add_event

router = APIRouter()


@router.get("", response_model=list[ApprovalOut])
def list_approvals(status: str | None = "pending", db: Session = Depends(get_db), limit: int = 100) -> list[Approval]:
    limit = min(max(limit, 1), 200)
    statement = select(Approval).order_by(desc(Approval.created_at)).limit(limit)
    if status:
        statement = statement.where(Approval.status == status)
    return list(db.scalars(statement).all())


@router.post("/{approval_id}/decision", response_model=ApprovalOut)
def decide_approval(
    approval_id: str,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> Approval:
    require_roles(principal, "reviewer")
    reviewer = principal.actor if principal.authenticated else payload.reviewer
    approval = db.get(Approval, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=409, detail="Approval has already been decided")
    if payload.decision not in {"approved", "rejected", "needs_revision"}:
        raise HTTPException(status_code=400, detail="Decision must be approved, rejected, or needs_revision")

    task = db.get(WorkflowTask, approval.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    approval.status = payload.decision
    approval.reviewer = reviewer
    approval.comment = payload.comment
    approval.decided_at = datetime.now(timezone.utc)

    if payload.decision == "approved":
        task.completed_at = datetime.now(timezone.utc)
        add_event(db, task, status="approved", progress=100, message=f"Approved by {reviewer}")
    elif payload.decision == "rejected":
        task.completed_at = datetime.now(timezone.utc)
        add_event(db, task, status="rejected", progress=100, message=f"Rejected by {reviewer}", level="warning")
    else:
        add_event(db, task, status="needs_revision", progress=95, message=f"Revision requested by {reviewer}", level="warning")

    record_audit(
        db,
        actor=reviewer,
        action=f"approval.{payload.decision}",
        resource_type="approval",
        resource_id=approval.id,
        detail={"task_id": task.id, "comment": payload.comment},
    )
    db.commit()
    db.refresh(approval)
    return approval
