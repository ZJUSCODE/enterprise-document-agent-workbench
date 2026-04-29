import hashlib
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


@dataclass(frozen=True)
class StoredObject:
    key: str
    size_bytes: int
    checksum_sha256: str


def safe_filename(filename: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
    cleaned = "".join(ch if ch in allowed else "_" for ch in filename).strip("._")
    return cleaned or "document"


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def save_upload(self, upload: UploadFile, prefix: str = "uploads") -> StoredObject:
        name = safe_filename(upload.filename or "document")
        key = f"{prefix}/{uuid4()}_{name}"
        if self.settings.storage_backend == "minio":
            return self._save_upload_minio(upload, key)
        return self._save_upload_local(upload, key)

    def save_bytes(self, key: str, content: bytes, content_type: str = "application/octet-stream") -> StoredObject:
        if self.settings.storage_backend == "minio":
            return self._save_bytes_minio(key, content, content_type)
        path = self._local_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return StoredObject(key=key, size_bytes=len(content), checksum_sha256=hashlib.sha256(content).hexdigest())

    def materialize(self, key: str) -> Path:
        if self.settings.storage_backend == "minio":
            return self._download_minio(key)
        return self._local_path(key)

    def read_bytes(self, key: str) -> bytes:
        if self.settings.storage_backend == "minio":
            return self._read_minio(key)
        return self._local_path(key).read_bytes()

    def _local_path(self, key: str) -> Path:
        root = self.settings.local_storage_dir.resolve()
        path = (root / key).resolve()
        if root not in path.parents and path != root:
            raise ValueError("Storage key escapes configured storage root")
        return path

    def _save_upload_local(self, upload: UploadFile, key: str) -> StoredObject:
        path = self._local_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        upload.file.seek(0)
        with path.open("wb") as destination:
            while chunk := upload.file.read(1024 * 1024):
                size += len(chunk)
                digest.update(chunk)
                destination.write(chunk)
        upload.file.seek(0)
        return StoredObject(key=key, size_bytes=size, checksum_sha256=digest.hexdigest())

    def _minio_client(self):
        try:
            from minio import Minio
        except ImportError as exc:
            raise RuntimeError("minio package is required when STORAGE_BACKEND=minio") from exc
        if not self.settings.minio_endpoint:
            raise RuntimeError("MINIO_ENDPOINT is required when STORAGE_BACKEND=minio")
        return Minio(
            self.settings.minio_endpoint,
            access_key=self.settings.minio_access_key,
            secret_key=self.settings.minio_secret_key,
            secure=self.settings.minio_secure,
        )

    def _ensure_bucket(self, client) -> None:
        bucket = self.settings.minio_bucket
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

    def _save_upload_minio(self, upload: UploadFile, key: str) -> StoredObject:
        digest = hashlib.sha256()
        size = 0
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = Path(temp.name)
            upload.file.seek(0)
            while chunk := upload.file.read(1024 * 1024):
                size += len(chunk)
                digest.update(chunk)
                temp.write(chunk)
        upload.file.seek(0)
        client = self._minio_client()
        self._ensure_bucket(client)
        client.fput_object(self.settings.minio_bucket, key, str(temp_path), content_type=upload.content_type)
        temp_path.unlink(missing_ok=True)
        return StoredObject(key=key, size_bytes=size, checksum_sha256=digest.hexdigest())

    def _save_bytes_minio(self, key: str, content: bytes, content_type: str) -> StoredObject:
        client = self._minio_client()
        self._ensure_bucket(client)
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = Path(temp.name)
            temp.write(content)
        client.fput_object(self.settings.minio_bucket, key, str(temp_path), content_type=content_type)
        temp_path.unlink(missing_ok=True)
        return StoredObject(key=key, size_bytes=len(content), checksum_sha256=hashlib.sha256(content).hexdigest())

    def _download_minio(self, key: str) -> Path:
        client = self._minio_client()
        target = self.settings.temp_dir / safe_filename(key.replace("/", "_"))
        target.parent.mkdir(parents=True, exist_ok=True)
        client.fget_object(self.settings.minio_bucket, key, str(target))
        return target

    def _read_minio(self, key: str) -> bytes:
        client = self._minio_client()
        response = client.get_object(self.settings.minio_bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()
