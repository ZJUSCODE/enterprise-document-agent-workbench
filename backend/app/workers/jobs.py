from app.services.workflow import run_document_task
from app.workers.celery_app import celery_app


@celery_app.task(name="app.process_document_task", bind=True)
def process_document_task(self, task_id: str) -> dict[str, str]:
    run_document_task(task_id)
    return {"task_id": task_id, "status": "submitted"}
