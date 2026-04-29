from fastapi import APIRouter

from app.api import routes_approvals, routes_audit, routes_files, routes_metrics, routes_rag, routes_tasks, routes_templates


api_router = APIRouter()
api_router.include_router(routes_files.router, prefix="/files", tags=["files"])
api_router.include_router(routes_tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(routes_approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(routes_audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(routes_metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(routes_templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(routes_rag.router, prefix="/rag", tags=["rag"])
