import uuid
from functools import lru_cache

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import AuthenticationError
from app.database.session import get_db_session
from app.models.user import User
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.finding_repository import FindingRepository, SQLAlchemyFindingRepository
from app.repositories.project_collaborator_repository import (
    ProjectCollaboratorRepository,
    SQLAlchemyProjectCollaboratorRepository,
)
from app.repositories.project_repository import SQLAlchemyProjectRepository
from app.repositories.scan_repository import SQLAlchemyScanRepository
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.scanner.ai import AIAnalyzer, AnthropicAIAnalyzer, NullAIAnalyzer
from app.security.jwt import TokenType, decode_token
from app.services.ai_service import AIService
from app.services.auth_service import AuthService
from app.services.collaborator_service import CollaboratorService
from app.services.dashboard_service import DashboardService
from app.services.project_service import ProjectService
from app.services.report_service import ReportService
from app.services.scan_service import ScanService

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(_oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    if token is None:
        raise AuthenticationError("Not authenticated.")
    payload = decode_token(token, expected_type=TokenType.ACCESS)
    user = await SQLAlchemyUserRepository(session).get_by_id(uuid.UUID(payload.sub))
    if user is None or not user.is_active:
        raise AuthenticationError("Invalid credentials.")
    return user


def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(SQLAlchemyUserRepository(session))


def get_project_collaborator_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ProjectCollaboratorRepository:
    return SQLAlchemyProjectCollaboratorRepository(session)


def get_project_service(
    session: AsyncSession = Depends(get_db_session),
    collaborator_repository: ProjectCollaboratorRepository = Depends(
        get_project_collaborator_repository
    ),
) -> ProjectService:
    return ProjectService(SQLAlchemyProjectRepository(session), collaborator_repository)


def get_collaborator_service(
    session: AsyncSession = Depends(get_db_session),
    project_service: ProjectService = Depends(get_project_service),
    collaborator_repository: ProjectCollaboratorRepository = Depends(
        get_project_collaborator_repository
    ),
) -> CollaboratorService:
    return CollaboratorService(
        project_service, collaborator_repository, SQLAlchemyUserRepository(session)
    )


def get_scan_service(session: AsyncSession = Depends(get_db_session)) -> ScanService:
    return ScanService(SQLAlchemyScanRepository(session), SQLAlchemyFindingRepository(session))


def get_report_service(session: AsyncSession = Depends(get_db_session)) -> ReportService:
    return ReportService(SQLAlchemyScanRepository(session), SQLAlchemyFindingRepository(session))


def get_dashboard_service(session: AsyncSession = Depends(get_db_session)) -> DashboardService:
    return DashboardService(DashboardRepository(session))


def get_finding_repository(session: AsyncSession = Depends(get_db_session)) -> FindingRepository:
    return SQLAlchemyFindingRepository(session)


@lru_cache
def get_ai_analyzer() -> AIAnalyzer:
    """Picks the `AIAnalyzer` implementation based on whether an Anthropic
    API key is configured. Cached process-wide: neither implementation
    carries per-request state, and constructing the Anthropic client is
    unnecessary work to repeat on every call."""
    settings = get_settings()
    if settings.anthropic_api_key:
        return AnthropicAIAnalyzer(settings.anthropic_api_key, settings.anthropic_model)
    return NullAIAnalyzer()


def get_ai_service(session: AsyncSession = Depends(get_db_session)) -> AIService:
    return AIService(SQLAlchemyFindingRepository(session), get_ai_analyzer())
