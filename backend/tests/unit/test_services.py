import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
)
from app.models.enums import ProjectRole, ScanTargetType, Severity
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.finding_repository import FindingFilter, SQLAlchemyFindingRepository
from app.repositories.project_collaborator_repository import (
    SQLAlchemyProjectCollaboratorRepository,
)
from app.repositories.project_repository import SQLAlchemyProjectRepository
from app.repositories.scan_repository import SQLAlchemyScanRepository
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.scanner.reports import ReportFormat
from app.services.auth_service import AuthService
from app.services.collaborator_service import CollaboratorService
from app.services.dashboard_service import DashboardService
from app.services.project_service import ProjectService
from app.services.report_service import ReportService
from app.services.scan_service import ScanService


@pytest.fixture
def auth_service(db_session: AsyncSession) -> AuthService:
    return AuthService(SQLAlchemyUserRepository(db_session))


@pytest.fixture
def project_service(db_session: AsyncSession) -> ProjectService:
    return ProjectService(
        SQLAlchemyProjectRepository(db_session),
        SQLAlchemyProjectCollaboratorRepository(db_session),
    )


@pytest.fixture
def collaborator_service(
    db_session: AsyncSession, project_service: ProjectService
) -> CollaboratorService:
    return CollaboratorService(
        project_service,
        SQLAlchemyProjectCollaboratorRepository(db_session),
        SQLAlchemyUserRepository(db_session),
    )


@pytest.fixture
def scan_service(db_session: AsyncSession) -> ScanService:
    return ScanService(
        SQLAlchemyScanRepository(db_session), SQLAlchemyFindingRepository(db_session)
    )


async def test_register_creates_user_and_rejects_duplicate_email(auth_service: AuthService) -> None:
    user = await auth_service.register("dev@example.com", "s3cret-pass", "Dev User")
    assert user.email == "dev@example.com"
    assert user.hashed_password != "s3cret-pass"

    with pytest.raises(ConflictError):
        await auth_service.register("dev@example.com", "other-pass", "Dev User 2")


async def test_login_succeeds_with_correct_credentials(auth_service: AuthService) -> None:
    await auth_service.register("dev@example.com", "s3cret-pass", "Dev User")
    tokens = await auth_service.login("dev@example.com", "s3cret-pass")
    assert tokens.access_token
    assert tokens.refresh_token


async def test_login_rejects_wrong_password(auth_service: AuthService) -> None:
    await auth_service.register("dev@example.com", "s3cret-pass", "Dev User")
    with pytest.raises(AuthenticationError):
        await auth_service.login("dev@example.com", "wrong-pass")


async def test_login_rejects_unknown_email(auth_service: AuthService) -> None:
    with pytest.raises(AuthenticationError):
        await auth_service.login("nobody@example.com", "whatever")


async def test_refresh_issues_new_tokens(auth_service: AuthService) -> None:
    await auth_service.register("dev@example.com", "s3cret-pass", "Dev User")
    tokens = await auth_service.login("dev@example.com", "s3cret-pass")
    refreshed = await auth_service.refresh(tokens.refresh_token)
    assert refreshed.access_token


async def test_project_service_create_list_get_delete(
    auth_service: AuthService, project_service: ProjectService
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")

    project = await project_service.create_project(owner.id, "My Project", "desc")
    assert project.name == "My Project"

    projects = await project_service.list_projects(owner.id)
    assert len(projects) == 1

    fetched = await project_service.get_project(owner.id, project.id)
    assert fetched.id == project.id

    await project_service.delete_project(owner.id, project.id)
    assert await project_service.list_projects(owner.id) == []


async def test_project_service_get_project_not_found(project_service: ProjectService) -> None:
    with pytest.raises(NotFoundError):
        await project_service.get_project(uuid.uuid4(), uuid.uuid4())


async def test_project_service_rejects_access_from_non_owner(
    auth_service: AuthService, project_service: ProjectService
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    other = await auth_service.register("other@example.com", "s3cret-pass", "Other")
    project = await project_service.create_project(owner.id, "My Project", None)

    with pytest.raises(AuthorizationError):
        await project_service.get_project(other.id, project.id)


async def test_scan_service_runs_scan_and_persists_findings(
    auth_service: AuthService, project_service: ProjectService, scan_service: ScanService, tmp_path
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    project = await project_service.create_project(owner.id, "My Project", None)

    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\n", encoding="utf-8")

    scan = await scan_service.run_scan(
        project_id=project.id,
        target_type=ScanTargetType.FILE,
        target_reference="vulnerable.py",
        scan_root=target,
    )

    assert scan.status.value == "completed"
    assert scan.files_scanned == 1
    assert scan.security_score is not None

    fetched = await scan_service.get_scan(scan.id)
    assert len(fetched.findings) == 1


async def test_scan_service_get_scan_not_found(scan_service: ScanService) -> None:
    with pytest.raises(NotFoundError):
        await scan_service.get_scan(uuid.uuid4())


async def test_report_service_exports_json_for_completed_scan(
    auth_service: AuthService,
    project_service: ProjectService,
    scan_service: ScanService,
    db_session: AsyncSession,
    tmp_path,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    project = await project_service.create_project(owner.id, "My Project", None)
    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\n", encoding="utf-8")
    scan = await scan_service.run_scan(
        project_id=project.id,
        target_type=ScanTargetType.FILE,
        target_reference="vulnerable.py",
        scan_root=target,
    )

    report_service = ReportService(
        SQLAlchemyScanRepository(db_session), SQLAlchemyFindingRepository(db_session)
    )
    content, content_type = await report_service.export(scan.id, project.name, ReportFormat.JSON)

    assert content_type == "application/json"
    assert b"CODE001" in content


async def test_finding_repository_filters_by_severity(
    auth_service: AuthService,
    project_service: ProjectService,
    scan_service: ScanService,
    db_session: AsyncSession,
    tmp_path,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    project = await project_service.create_project(owner.id, "My Project", None)
    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\nhashlib.md5(x)\n", encoding="utf-8")
    await scan_service.run_scan(
        project_id=project.id,
        target_type=ScanTargetType.FILE,
        target_reference="vulnerable.py",
        scan_root=target,
    )

    finding_repository = SQLAlchemyFindingRepository(db_session)
    critical_only = await finding_repository.search(
        FindingFilter(project_id=project.id, severity=Severity.CRITICAL)
    )
    assert all(f.severity.value == "critical" for f in critical_only)


async def test_dashboard_service_summary_reflects_scan_results(
    auth_service: AuthService,
    project_service: ProjectService,
    scan_service: ScanService,
    db_session: AsyncSession,
    tmp_path,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    project = await project_service.create_project(owner.id, "My Project", None)
    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\n", encoding="utf-8")
    await scan_service.run_scan(
        project_id=project.id,
        target_type=ScanTargetType.FILE,
        target_reference="vulnerable.py",
        scan_root=target,
    )

    dashboard_service = DashboardService(DashboardRepository(db_session))
    summary = await dashboard_service.get_summary(owner.id)

    assert summary.total_projects == 1
    assert summary.total_scans == 1
    assert summary.total_findings == 1
    assert summary.critical_count == 1

    top_vulns = await dashboard_service.get_top_vulnerabilities(owner.id)
    assert top_vulns[0].label == "Unsafe Eval / Code Injection"

    top_files = await dashboard_service.get_top_files(owner.id)
    assert top_files[0].count == 1


async def test_owner_can_add_and_list_collaborators(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    collaborator_user = await auth_service.register("teammate@example.com", "s3cret-pass", "Mate")
    project = await project_service.create_project(owner.id, "Shared Project", None)

    added = await collaborator_service.add_collaborator(
        owner.id, project.id, "teammate@example.com", ProjectRole.EDITOR
    )
    assert added.user_id == collaborator_user.id
    assert added.role == ProjectRole.EDITOR
    assert added.user.email == "teammate@example.com"

    collaborators = await collaborator_service.list_collaborators(owner.id, project.id)
    assert len(collaborators) == 1
    assert collaborators[0].user.full_name == "Mate"


async def test_adding_the_same_collaborator_twice_conflicts(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    await auth_service.register("teammate@example.com", "s3cret-pass", "Mate")
    project = await project_service.create_project(owner.id, "Shared Project", None)

    await collaborator_service.add_collaborator(
        owner.id, project.id, "teammate@example.com", ProjectRole.VIEWER
    )
    with pytest.raises(ConflictError):
        await collaborator_service.add_collaborator(
            owner.id, project.id, "teammate@example.com", ProjectRole.EDITOR
        )


async def test_non_owner_cannot_add_collaborators(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    editor = await auth_service.register("editor@example.com", "s3cret-pass", "Editor")
    await auth_service.register("third@example.com", "s3cret-pass", "Third")
    project = await project_service.create_project(owner.id, "Shared Project", None)
    await collaborator_service.add_collaborator(
        owner.id, project.id, "editor@example.com", ProjectRole.EDITOR
    )

    with pytest.raises(AuthorizationError):
        await collaborator_service.add_collaborator(
            editor.id, project.id, "third@example.com", ProjectRole.VIEWER
        )


async def test_owner_can_update_and_remove_collaborator(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    await auth_service.register("teammate@example.com", "s3cret-pass", "Mate")
    project = await project_service.create_project(owner.id, "Shared Project", None)
    added = await collaborator_service.add_collaborator(
        owner.id, project.id, "teammate@example.com", ProjectRole.VIEWER
    )

    updated = await collaborator_service.update_role(
        owner.id, project.id, added.user_id, ProjectRole.EDITOR
    )
    assert updated.role == ProjectRole.EDITOR

    await collaborator_service.remove_collaborator(owner.id, project.id, added.user_id)
    assert await collaborator_service.list_collaborators(owner.id, project.id) == []


async def test_viewer_can_view_but_not_required_editor_action(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    viewer = await auth_service.register("viewer@example.com", "s3cret-pass", "Viewer")
    project = await project_service.create_project(owner.id, "Shared Project", None)
    await collaborator_service.add_collaborator(
        owner.id, project.id, "viewer@example.com", ProjectRole.VIEWER
    )

    # Viewers can read the project...
    fetched = await project_service.get_project(viewer.id, project.id)
    assert fetched.id == project.id

    # ...but not perform editor-gated actions (e.g. running a scan).
    with pytest.raises(AuthorizationError):
        await project_service.require_editor(viewer.id, project.id)


async def test_editor_passes_require_editor_check(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    editor = await auth_service.register("editor@example.com", "s3cret-pass", "Editor")
    project = await project_service.create_project(owner.id, "Shared Project", None)
    await collaborator_service.add_collaborator(
        owner.id, project.id, "editor@example.com", ProjectRole.EDITOR
    )

    fetched = await project_service.require_editor(editor.id, project.id)
    assert fetched.id == project.id


async def test_collaborator_cannot_delete_project(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    editor = await auth_service.register("editor@example.com", "s3cret-pass", "Editor")
    project = await project_service.create_project(owner.id, "Shared Project", None)
    await collaborator_service.add_collaborator(
        owner.id, project.id, "editor@example.com", ProjectRole.EDITOR
    )

    with pytest.raises(AuthorizationError):
        await project_service.delete_project(editor.id, project.id)


async def test_list_projects_includes_collaborated_projects(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    collaborator_user = await auth_service.register("teammate@example.com", "s3cret-pass", "Mate")
    project = await project_service.create_project(owner.id, "Shared Project", None)
    await collaborator_service.add_collaborator(
        owner.id, project.id, "teammate@example.com", ProjectRole.VIEWER
    )

    visible_to_collaborator = await project_service.list_projects(collaborator_user.id)
    assert [p.id for p in visible_to_collaborator] == [project.id]


async def test_dashboard_includes_collaborated_projects(
    auth_service: AuthService,
    project_service: ProjectService,
    collaborator_service: CollaboratorService,
    scan_service: ScanService,
    tmp_path,
    db_session: AsyncSession,
) -> None:
    owner = await auth_service.register("owner@example.com", "s3cret-pass", "Owner")
    collaborator_user = await auth_service.register("teammate@example.com", "s3cret-pass", "Mate")
    project = await project_service.create_project(owner.id, "Shared Project", None)
    await collaborator_service.add_collaborator(
        owner.id, project.id, "teammate@example.com", ProjectRole.EDITOR
    )

    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\n", encoding="utf-8")
    await scan_service.run_scan(
        project_id=project.id,
        target_type=ScanTargetType.FILE,
        target_reference="vulnerable.py",
        scan_root=target,
    )

    dashboard_service = DashboardService(DashboardRepository(db_session))
    summary = await dashboard_service.get_summary(collaborator_user.id)

    assert summary.total_projects == 1
    assert summary.total_scans == 1
    assert summary.total_findings == 1
