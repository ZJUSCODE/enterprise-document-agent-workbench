from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import Principal, get_current_principal, require_roles
from app.db.session import get_db
from app.models import WorkflowTask
from app.schemas.rag import RagAnswerOut, RagHitOut, RagQuery, RagReindexOut
from app.services.parser import DocumentParser
from app.services.rag import RagService
from app.services.storage import StorageService

router = APIRouter()


@router.post("/query", response_model=RagAnswerOut)
def query_rag(payload: RagQuery, db: Session = Depends(get_db)) -> RagAnswerOut:
    rag = RagService()
    hits = rag.search(
        db,
        question=payload.question,
        top_k=payload.top_k,
        document_type=payload.document_type,
        file_id=payload.file_id,
    )
    answer = rag.answer(payload.question, hits)
    return RagAnswerOut(
        question=payload.question,
        answer=answer,
        hits=[
            RagHitOut(
                chunk_id=hit.chunk_id,
                file_id=hit.file_id,
                task_id=hit.task_id,
                document_type=hit.document_type,
                score=hit.score,
                text=hit.text,
                metadata=hit.metadata,
            )
            for hit in hits
        ],
    )


@router.post("/reindex", response_model=RagReindexOut)
def reindex_rag(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> RagReindexOut:
    require_roles(principal, "operator")
    storage = StorageService()
    parser = DocumentParser()
    rag = RagService()
    tasks = list(
        db.scalars(
            select(WorkflowTask)
            .where(WorkflowTask.classified_as.is_not(None))
            .options(selectinload(WorkflowTask.file))
        ).all()
    )
    indexed_tasks = 0
    indexed_chunks = 0
    for task in tasks:
        if not task.file:
            continue
        try:
            parsed = parser.parse(storage.materialize(task.file.storage_key), task.file.original_filename)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to parse task {task.id}: {exc}") from exc
        indexed_chunks += rag.index_document(
            db,
            file_id=task.file_id,
            task_id=task.id,
            text=parsed.text,
            document_type=task.classified_as,
            metadata={"filename": task.file.original_filename, "parser_name": parsed.parser_name, "reindexed": True},
        )
        indexed_tasks += 1
    db.commit()
    return RagReindexOut(indexed_tasks=indexed_tasks, indexed_chunks=indexed_chunks)
