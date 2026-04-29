from datetime import datetime, timezone
from time import perf_counter
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models import Approval, DocumentFile, ResultVersion, TaskEvent, TemplateDefinition, WorkflowTask
from app.services.agents import AgentTraceRecorder, RiskReviewAgent
from app.services.audit import record_audit
from app.services.classifier import classify_document
from app.services.extractor import ExtractorService
from app.services.parser import DocumentParser
from app.services.rag import RagService
from app.services.storage import StorageService
from app.services.templates import TemplateRenderer


TERMINAL_STATUSES = {"approved", "completed", "rejected", "failed"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_workflow_task(
    db: Session,
    *,
    file_id: str,
    template_id: str,
    task_type: str,
    priority: int,
    submitted_by: str,
) -> WorkflowTask:
    settings = get_settings()
    file = db.get(DocumentFile, file_id)
    if not file:
        raise ValueError(f"Document file does not exist: {file_id}")
    template = db.get(TemplateDefinition, template_id)
    if not template:
        raise ValueError(f"Template does not exist: {template_id}")
    task = WorkflowTask(
        file_id=file_id,
        template_id=template_id,
        task_type=task_type,
        priority=priority,
        submitted_by=submitted_by,
        max_retries=settings.max_task_retries,
    )
    db.add(task)
    db.flush()
    add_event(db, task, status="queued", progress=0, message="Task created and queued")
    record_audit(
        db,
        actor=submitted_by,
        action="task.created",
        resource_type="task",
        resource_id=task.id,
        detail={"file_id": file_id, "template_id": template_id},
    )
    db.commit()
    db.refresh(task)
    return task


def add_event(db: Session, task: WorkflowTask, *, status: str, progress: int, message: str, level: str = "info") -> TaskEvent:
    task.status = status
    task.progress = progress
    task.updated_at = utc_now()
    event = TaskEvent(task_id=task.id, status=status, progress=progress, message=message, level=level)
    db.add(event)
    db.flush()
    return event


def run_document_task(task_id: str) -> None:
    attempts = 0
    while True:
        try:
            _process_once(task_id)
            return
        except Exception as exc:
            attempts += 1
            with SessionLocal() as db:
                task = db.get(WorkflowTask, task_id)
                if not task:
                    return
                task.retry_count += 1
                if task.retry_count <= task.max_retries:
                    add_event(
                        db,
                        task,
                        status="queued",
                        progress=min(task.progress, 20),
                        message=f"Task failed and will retry ({task.retry_count}/{task.max_retries}): {exc}",
                        level="warning",
                    )
                    record_audit(
                        db,
                        actor="worker",
                        action="task.retry_scheduled",
                        resource_type="task",
                        resource_id=task.id,
                        detail={"error": str(exc), "attempt": attempts},
                    )
                    db.commit()
                    continue
                task.error_message = str(exc)
                task.completed_at = utc_now()
                add_event(db, task, status="failed", progress=100, message=f"Task failed: {exc}", level="error")
                record_audit(
                    db,
                    actor="worker",
                    action="task.failed",
                    resource_type="task",
                    resource_id=task.id,
                    detail={"error": str(exc)},
                )
                db.commit()
                return


def _process_once(task_id: str) -> None:
    storage = StorageService()
    parser = DocumentParser()
    extractor = ExtractorService()
    renderer = TemplateRenderer()
    rag = RagService()
    trace = AgentTraceRecorder()
    risk_agent = RiskReviewAgent()
    settings = get_settings()

    with SessionLocal() as db:
        task = db.scalar(
            select(WorkflowTask)
            .where(WorkflowTask.id == task_id)
            .options(selectinload(WorkflowTask.file), selectinload(WorkflowTask.template))
        )
        if not task:
            raise ValueError(f"Task does not exist: {task_id}")
        if task.status in TERMINAL_STATUSES:
            return
        task.started_at = task.started_at or utc_now()
        add_event(db, task, status="running", progress=10, message="Worker started")
        record_audit(db, actor="worker", action="task.started", resource_type="task", resource_id=task.id)
        db.commit()

        file = task.file
        template = task.template
        source_path = storage.materialize(file.storage_key)

        step_started = utc_now().isoformat()
        step_tick = perf_counter()
        parsed = parser.parse(source_path, file.original_filename)
        file.parser_name = parsed.parser_name
        file.parse_warnings = parsed.warnings
        file.metadata_json = {**(file.metadata_json or {}), **parsed.metadata}
        file.status = "parsed"
        task.table_data = _normalize_tables(parsed.tables)
        trace.record(
            task,
            agent="document_intake_agent",
            tool=parsed.parser_name,
            input_summary=f"file={file.original_filename}",
            output_summary=f"text_chars={len(parsed.text)}, tables={len(parsed.tables)}, warnings={len(parsed.warnings)}",
            started_at=step_started,
            duration_ms=int((perf_counter() - step_tick) * 1000),
        )
        add_event(db, task, status="parsing", progress=30, message=f"Parsed with {parsed.parser_name}")
        db.commit()

        step_started = utc_now().isoformat()
        step_tick = perf_counter()
        document_type, confidence = classify_document(parsed.text, file.original_filename)
        task.classified_as = document_type
        task.summary = {**(task.summary or {}), "classification_confidence": confidence}
        trace.record(
            task,
            agent="router_agent",
            tool="keyword_classifier",
            input_summary=f"filename={file.original_filename}",
            output_summary=f"document_type={document_type}, confidence={confidence:.2f}",
            started_at=step_started,
            duration_ms=int((perf_counter() - step_tick) * 1000),
        )
        add_event(db, task, status="classifying", progress=45, message=f"Classified as {document_type} ({confidence:.2f})")
        db.commit()

        step_started = utc_now().isoformat()
        step_tick = perf_counter()
        chunk_count = rag.index_document(
            db,
            file_id=file.id,
            task_id=task.id,
            text=parsed.text,
            document_type=document_type,
            metadata={"filename": file.original_filename, "parser_name": parsed.parser_name},
        )
        trace.record(
            task,
            agent="rag_index_agent",
            tool="local_lexical_index",
            input_summary=f"text_chars={len(parsed.text)}",
            output_summary=f"indexed_chunks={chunk_count}",
            started_at=step_started,
            duration_ms=int((perf_counter() - step_tick) * 1000),
        )
        add_event(db, task, status="indexing", progress=55, message=f"Indexed {chunk_count} RAG chunks")
        db.commit()

        step_started = utc_now().isoformat()
        step_tick = perf_counter()
        result = extractor.extract(parsed, document_type=document_type, template_id=template.id)
        task.extracted_fields = result.fields
        task.summary = {**(task.summary or {}), **result.summary, "quality_score": result.quality_score}
        task.anomalies = result.anomalies
        trace.record(
            task,
            agent="extraction_agent",
            tool="llm_structured_output_or_rules",
            input_summary=f"document_type={document_type}, template={template.id}",
            output_summary=f"fields={len(result.fields)}, anomalies={len(result.anomalies)}, quality={result.quality_score:.3f}",
            started_at=step_started,
            duration_ms=int((perf_counter() - step_tick) * 1000),
        )
        add_event(db, task, status="extracting", progress=70, message="Structured extraction completed")
        db.commit()

        step_started = utc_now().isoformat()
        step_tick = perf_counter()
        task.anomalies, risk_summary = risk_agent.review(document_type=document_type, text=parsed.text, anomalies=task.anomalies)
        task.summary = {**(task.summary or {}), "risk_review": risk_summary}
        trace.record(
            task,
            agent="risk_review_agent",
            tool="contract_risk_rules",
            input_summary=f"document_type={document_type}, current_anomalies={len(result.anomalies)}",
            output_summary=f"risk_level={risk_summary['risk_level']}, risk_count={risk_summary['risk_count']}",
            started_at=step_started,
            duration_ms=int((perf_counter() - step_tick) * 1000),
        )
        add_event(db, task, status="reviewing", progress=78, message="Risk review agent completed")
        db.commit()

        step_started = utc_now().isoformat()
        step_tick = perf_counter()
        task.generated_artifact_key = renderer.render_task(task, template)
        task.result_version += 1
        db.add(
            ResultVersion(
                task_id=task.id,
                version=task.result_version,
                artifact_key=task.generated_artifact_key,
                extracted_fields=task.extracted_fields,
                summary=task.summary,
                anomalies=task.anomalies,
                created_by="worker",
            )
        )
        trace.record(
            task,
            agent="template_agent",
            tool="jinja_renderer",
            input_summary=f"template={template.id}",
            output_summary=f"artifact_key={task.generated_artifact_key}",
            started_at=step_started,
            duration_ms=int((perf_counter() - step_tick) * 1000),
        )
        add_event(db, task, status="generating", progress=86, message="Template artifact generated")
        db.commit()

        step_started = utc_now().isoformat()
        step_tick = perf_counter()
        if settings.approval_required:
            db.add(Approval(task_id=task.id, status="pending"))
            trace.record(
                task,
                agent="approval_coordinator_agent",
                tool="human_approval_queue",
                input_summary=f"task={task.id}",
                output_summary="approval_status=pending",
                started_at=step_started,
                duration_ms=int((perf_counter() - step_tick) * 1000),
            )
            add_event(db, task, status="waiting_approval", progress=95, message="Waiting for human approval")
            record_audit(db, actor="worker", action="approval.created", resource_type="task", resource_id=task.id)
        else:
            task.completed_at = utc_now()
            trace.record(
                task,
                agent="approval_coordinator_agent",
                tool="approval_bypass",
                input_summary=f"task={task.id}",
                output_summary="approval_required=false",
                started_at=step_started,
                duration_ms=int((perf_counter() - step_tick) * 1000),
            )
            add_event(db, task, status="completed", progress=100, message="Task completed without approval requirement")
        record_audit(
            db,
            actor="worker",
            action="task.processed",
            resource_type="task",
            resource_id=task.id,
            detail={"document_type": document_type, "artifact_key": task.generated_artifact_key},
        )
        db.commit()


def dispatch_task(task_id: str, background_tasks=None) -> None:
    settings = get_settings()
    if settings.queue_backend == "celery":
        from app.workers.jobs import process_document_task

        process_document_task.delay(task_id)
        return
    if background_tasks is not None:
        background_tasks.add_task(run_document_task, task_id)
        return
    run_document_task(task_id)


def revise_task_result(
    db: Session,
    *,
    task: WorkflowTask,
    revised_by: str,
    extracted_fields: dict | None = None,
    summary: dict | None = None,
    anomalies: list[dict] | None = None,
    comment: str | None = None,
) -> WorkflowTask:
    task.extracted_fields = extracted_fields if extracted_fields is not None else task.extracted_fields
    task.summary = summary if summary is not None else task.summary
    task.anomalies = anomalies if anomalies is not None else task.anomalies
    task.completed_at = None

    renderer = TemplateRenderer()
    trace = AgentTraceRecorder()
    step_started = utc_now().isoformat()
    step_tick = perf_counter()
    task.generated_artifact_key = renderer.render_task(task, task.template, output_format="markdown")
    task.result_version += 1
    db.add(
        ResultVersion(
            task_id=task.id,
            version=task.result_version,
            artifact_key=task.generated_artifact_key,
            extracted_fields=task.extracted_fields,
            summary=task.summary,
            anomalies=task.anomalies,
            created_by=revised_by,
        )
    )

    pending_approval = next((approval for approval in task.approvals if approval.status == "pending"), None)
    if pending_approval is None:
        db.add(Approval(task_id=task.id, status="pending"))

    add_event(
        db,
        task,
        status="waiting_approval",
        progress=95,
        message=f"Result revised by {revised_by}; waiting for approval",
    )
    trace.record(
        task,
        agent="human_revision_agent",
        tool="manual_result_editor",
        input_summary=f"comment={comment or ''}",
        output_summary=f"new_version={task.result_version}",
        started_at=step_started,
        duration_ms=int((perf_counter() - step_tick) * 1000),
    )
    record_audit(
        db,
        actor=revised_by,
        action="task.result_revised",
        resource_type="task",
        resource_id=task.id,
        detail={"version": task.result_version, "comment": comment},
    )
    db.commit()
    db.refresh(task)
    return task


def _normalize_tables(tables: Iterable[dict]) -> list[dict]:
    normalized = []
    for table in tables:
        rows = table.get("rows", [])
        normalized.append({"name": table.get("name", "table"), "row_count": len(rows), "rows": rows[:100]})
    return normalized
