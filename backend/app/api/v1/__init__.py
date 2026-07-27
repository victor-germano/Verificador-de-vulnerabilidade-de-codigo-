from fastapi import APIRouter

from app.api.v1 import ai, auth, dashboard, findings, projects, reports, scans

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(scans.router)
api_router.include_router(findings.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
api_router.include_router(ai.router)

__all__ = ["api_router"]
