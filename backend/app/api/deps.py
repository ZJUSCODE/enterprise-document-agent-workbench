from app.services.storage import StorageService


def get_storage() -> StorageService:
    return StorageService()
