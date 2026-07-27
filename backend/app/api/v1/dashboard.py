from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_dashboard_service
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, SeverityTrendPoint, TopItem
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummary:
    return await dashboard_service.get_summary(current_user.id)


@router.get("/trend", response_model=list[SeverityTrendPoint])
async def get_trend(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> list[SeverityTrendPoint]:
    return await dashboard_service.get_trend(current_user.id, days=days)


@router.get("/top-vulnerabilities", response_model=list[TopItem])
async def get_top_vulnerabilities(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> list[TopItem]:
    return await dashboard_service.get_top_vulnerabilities(current_user.id, limit=limit)


@router.get("/top-files", response_model=list[TopItem])
async def get_top_files(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> list[TopItem]:
    return await dashboard_service.get_top_files(current_user.id, limit=limit)
