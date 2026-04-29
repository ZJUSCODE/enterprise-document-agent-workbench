import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal, get_db
from app.models import ResultVersion, TaskEvent, WorkflowTask
from app.schemas.tasks import (
    BatchTaskCreate,
    ResultVersionOut,
    TaskCreate,
    TaskDetailOut,
    TaskEventOut,
    TaskOut,
    TaskRevision,
)
from app.core.security import Principal, get_current_principal, require_roles
from app.services.storage import StorageService
from app.services.templates import TemplateRenderer
from app.services.workflow import create_workflow_task, dispatch_task, revise_task_result

router = APIRouter()


@router.post("", response_model=TaskOut, status_code=201)
def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> WorkflowTask:
    require_roles(principal, "operator")
    submitted_by = principal.actor if principal.authenticated else payload.submitted_by
    try:
        task = create_workflow_task(
            db,
            file_id=payload.file_id,
            template_id=payload.template_id,
            task_type=payload.task_type,
            priority=payload.priority,
            submitted_by=submitted_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    dispatch_task(task.id, background_tasks)
    return task


@router.post("/batch", response_model=list[TaskOut], status_code=201)
def create_batch_tasks(
    payload: BatchTaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> list[WorkflowTask]:
    require_roles(principal, "operator")
    submitted_by = principal.actor if principal.authenticated else payload.submitted_by
    tasks = []
    for file_id in payload.file_ids:
        try:
            task = create_workflow_task(
                db,
                file_id=file_id,
                template_id=payload.template_id,
                task_type=payload.task_type,
                priority=payload.priority,
                submitted_by=submitted_by,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        dispatch_task(task.id, background_tasks)
        tasks.append(task)
    return tasks


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[WorkflowTask]:
    limit = min(max(limit, 1), 200)
    statement = select(WorkflowTask).order_by(desc(WorkflowTask.created_at)).offset(offset).limit(limit)
    if status:
        statement = statement.where(WorkflowTask.status == status)
    return list(db.scalars(statement).all())


@router.get("/{task_id}", response_model=TaskDetailOut)
def get_task(task_id: str, db: Session = Depends(get_db)) -> WorkflowTask:
    task = db.scalar(
        select(WorkflowTask)
        .where(WorkflowTask.id == task_id)
        .options(selectinload(WorkflowTask.events), selectinload(WorkflowTask.approvals))
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.events.sort(key=lambda event: event.created_at)
    task.approvals.sort(key=lambda approval: approval.created_at)
    return task


@router.get("/{task_id}/events", response_model=list[TaskEventOut])
def get_task_events(task_id: str, db: Session = Depends(get_db)) -> list[TaskEvent]:
    task = db.get(WorkflowTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return list(db.scalars(select(TaskEvent).where(TaskEvent.task_id == task_id).order_by(TaskEvent.created_at)).all())


@router.get("/{task_id}/versions", response_model=list[ResultVersionOut])
def get_task_versions(task_id: str, db: Session = Depends(get_db)) -> list[ResultVersion]:
    task = db.get(WorkflowTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return list(db.scalars(select(ResultVersion).where(ResultVersion.task_id == task_id).order_by(ResultVersion.version)).all())


@router.patch("/{task_id}/result", response_model=TaskDetailOut)
def revise_task(
    task_id: str,
    payload: TaskRevision,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> WorkflowTask:
    require_roles(principal, "reviewer")
    revised_by = principal.actor if principal.authenticated else payload.revised_by
    task = db.scalar(
        select(WorkflowTask)
        .where(WorkflowTask.id == task_id)
        .options(
            selectinload(WorkflowTask.file),
            selectinload(WorkflowTask.template),
            selectinload(WorkflowTask.approvals),
            selectinload(WorkflowTask.events),
        )
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status in {"failed", "rejected"}:
        raise HTTPException(status_code=409, detail=f"Cannot revise task in status {task.status}")
    revised = revise_task_result(
        db,
        task=task,
        revised_by=revised_by,
        extracted_fields=payload.extracted_fields,
        summary=payload.summary,
        anomalies=payload.anomalies,
        comment=payload.comment,
    )
    revised.events.sort(key=lambda event: event.created_at)
    revised.approvals.sort(key=lambda approval: approval.created_at)
    return revised


@router.get("/{task_id}/events/stream")
async def stream_task_events(task_id: str, request: Request) -> StreamingResponse:
    async def event_generator():
        seen_ids: set[str] = set()
        while True:
            if await request.is_disconnected():
                return
            with SessionLocal() as db:
                task = db.get(WorkflowTask, task_id)
                if not task:
                    yield "event: error\ndata: {\"detail\":\"Task not found\"}\n\n"
                    return
                events = list(
                    db.scalars(select(TaskEvent).where(TaskEvent.task_id == task_id).order_by(TaskEvent.created_at)).all()
                )
                for event in events:
                    if event.id in seen_ids:
                        continue
                    seen_ids.add(event.id)
                    payload = {
                        "id": event.id,
                        "status": event.status,
                        "progress": event.progress,
                        "level": event.level,
                        "message": event.message,
                        "created_at": event.created_at.isoformat(),
                    }
                    yield f"event: task_event\ndata: {json.dumps(payload)}\n\n"
                if task.status in {"approved", "completed", "rejected", "failed"}:
                    yield f"event: done\ndata: {json.dumps({'status': task.status})}\n\n"
                    return
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{task_id}/export")
def export_task_artifact(task_id: str, format: str = "markdown", db: Session = Depends(get_db)) -> Response:
    export_format = format.lower()
    if export_format not in {"markdown", "docx", "pdf", "txt"}:
        raise HTTPException(status_code=400, detail="format must be markdown, docx, pdf, or txt")
    task = db.scalar(
        select(WorkflowTask)
        .where(WorkflowTask.id == task_id)
        .options(selectinload(WorkflowTask.file), selectinload(WorkflowTask.template))
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.generated_artifact_key:
        raise HTTPException(status_code=409, detail="Task artifact is not ready")
    renderer = TemplateRenderer()
    if export_format == "markdown" and task.generated_artifact_key:
        storage = StorageService()
        content = storage.read_bytes(task.generated_artifact_key)
        content_type = "text/markdown; charset=utf-8"
    else:
        content, content_type = renderer.render_bytes(task, task.template, export_format)
    filename = f"{task.id}.{renderer.extension(export_format)}"
    return Response(
        content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
