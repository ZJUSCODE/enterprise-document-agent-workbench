from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import DocumentFile
from app.schemas.files import DocumentFileOut
from app.core.security import Principal, get_current_principal, require_roles
from app.services.audit import record_audit
from app.services.storage import StorageService

router = APIRouter()


@router.post("/upload", response_model=DocumentFileOut, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    actor: str = Form("system"),
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> DocumentFile:
    require_roles(principal, "operator")
    audit_actor = principal.actor if principal.authenticated else actor
    storage = StorageService()
    stored = storage.save_upload(file)
    record = DocumentFile(
        original_filename=file.filename or "document",
        content_type=file.content_type,
        size_bytes=stored.size_bytes,
        checksum_sha256=stored.checksum_sha256,
        storage_key=stored.key,
        created_by=audit_actor,
        metadata_json={"source": "upload"},
    )
    db.add(record)
    db.flush()
    record_audit(
        db,
        actor=audit_actor,
        action="file.uploaded",
        resource_type="file",
        resource_id=record.id,
        detail={"filename": record.original_filename, "size_bytes": record.size_bytes},
    )
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[DocumentFileOut])
def list_files(db: Session = Depends(get_db), limit: int = 50, offset: int = 0) -> list[DocumentFile]:
    limit = min(max(limit, 1), 200)
    return list(db.scalars(select(DocumentFile).order_by(desc(DocumentFile.created_at)).offset(offset).limit(limit)).all())


@router.get("/{file_id}", response_model=DocumentFileOut)
def get_file(file_id: str, db: Session = Depends(get_db)) -> DocumentFile:
    record = db.get(DocumentFile, file_id)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    return record
