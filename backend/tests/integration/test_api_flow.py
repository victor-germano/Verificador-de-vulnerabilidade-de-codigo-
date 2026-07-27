from pathlib import Path

from httpx import AsyncClient

from app.api.v1 import scans as scans_router


async def _register_and_login(client: AsyncClient, email: str = "dev@example.com") -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "s3cret-pass", "full_name": "Dev User"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "s3cret-pass"}
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_register_login_and_access_protected_route(client: AsyncClient) -> None:
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "dev@example.com", "password": "s3cret-pass", "full_name": "Dev User"},
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["email"] == "dev@example.com"

    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "dev@example.com", "password": "s3cret-pass"}
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]


async def test_me_returns_current_user_and_requires_auth(client: AsyncClient) -> None:
    unauthenticated_resp = await client.get("/api/v1/auth/me")
    assert unauthenticated_resp.status_code == 401

    headers = await _register_and_login(client)
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "dev@example.com"


async def test_login_with_wrong_password_returns_401(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dev@example.com", "password": "s3cret-pass", "full_name": "Dev User"},
    )
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "dev@example.com", "password": "wrong"}
    )
    assert resp.status_code == 401


async def test_projects_require_authentication(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/projects")
    assert resp.status_code == 401


async def test_create_and_list_projects(client: AsyncClient) -> None:
    headers = await _register_and_login(client)

    create_resp = await client.post(
        "/api/v1/projects", json={"name": "Demo Project", "description": "desc"}, headers=headers
    )
    assert create_resp.status_code == 201
    project = create_resp.json()

    list_resp = await client.get("/api/v1/projects", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id"] == project["id"]


async def test_project_not_owned_returns_403(client: AsyncClient) -> None:
    headers_a = await _register_and_login(client, "a@example.com")
    headers_b = await _register_and_login(client, "b@example.com")

    create_resp = await client.post(
        "/api/v1/projects", json={"name": "A's project"}, headers=headers_a
    )
    project_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/projects/{project_id}", headers=headers_b)
    assert resp.status_code == 403


async def test_upload_and_scan_end_to_end(client: AsyncClient) -> None:
    headers = await _register_and_login(client)
    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Demo Project"}, headers=headers
    )
    project_id = project_resp.json()["id"]

    vulnerable_source = b"eval(user_input)\n"
    scan_resp = await client.post(
        f"/api/v1/scans/upload?project_id={project_id}",
        headers=headers,
        files={"file": ("vulnerable.py", vulnerable_source, "text/x-python")},
    )
    assert scan_resp.status_code == 201
    scan = scan_resp.json()
    assert scan["status"] == "completed"
    assert scan["files_scanned"] == 1

    findings_resp = await client.get(f"/api/v1/findings?project_id={project_id}", headers=headers)
    assert findings_resp.status_code == 200
    findings = findings_resp.json()
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "CODE001"

    dashboard_resp = await client.get("/api/v1/dashboard/summary", headers=headers)
    assert dashboard_resp.status_code == 200
    summary = dashboard_resp.json()
    assert summary["total_projects"] == 1
    assert summary["total_findings"] == 1

    report_resp = await client.get(f"/api/v1/reports/{scan['id']}?format=json", headers=headers)
    assert report_resp.status_code == 200
    assert report_resp.headers["content-type"].startswith("application/json")


async def test_git_scan_rejects_non_http_url(client: AsyncClient) -> None:
    headers = await _register_and_login(client)
    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Demo Project"}, headers=headers
    )
    project_id = project_resp.json()["id"]

    resp = await client.post(
        "/api/v1/scans/git",
        headers=headers,
        json={"project_id": project_id, "repository_url": "ftp://example.com/repo.git"},
    )
    assert resp.status_code == 422


async def test_git_scan_clones_and_analyzes_repository(
    client: AsyncClient, tmp_path, monkeypatch
) -> None:
    def fake_clone_repository(url: str, destination: Path, access_token: str | None = None) -> Path:
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "app.py").write_text("eval(user_input)\n", encoding="utf-8")
        return destination

    monkeypatch.setattr(scans_router, "clone_repository", fake_clone_repository)

    headers = await _register_and_login(client)
    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Demo Project"}, headers=headers
    )
    project_id = project_resp.json()["id"]

    resp = await client.post(
        "/api/v1/scans/git",
        headers=headers,
        json={
            "project_id": project_id,
            "repository_url": "https://github.com/example/vulnerable-app.git",
        },
    )
    assert resp.status_code == 201
    scan = resp.json()
    assert scan["target_type"] == "git_repository"
    assert scan["status"] == "completed"
    assert scan["files_scanned"] == 1


async def test_git_scan_with_access_token_is_passed_through_but_never_persisted(
    client: AsyncClient, monkeypatch
) -> None:
    captured: dict = {}

    def fake_clone_repository(url: str, destination: Path, access_token: str | None = None) -> Path:
        captured["access_token"] = access_token
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "app.py").write_text("eval(user_input)\n", encoding="utf-8")
        return destination

    monkeypatch.setattr(scans_router, "clone_repository", fake_clone_repository)

    headers = await _register_and_login(client)
    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Demo Project"}, headers=headers
    )
    project_id = project_resp.json()["id"]

    resp = await client.post(
        "/api/v1/scans/git",
        headers=headers,
        json={
            "project_id": project_id,
            "repository_url": "https://github.com/example/private-repo.git",
            "access_token": "ghp_secretTOKEN123",
        },
    )
    assert resp.status_code == 201
    scan = resp.json()

    # The token reached clone_repository...
    assert captured["access_token"] == "ghp_secretTOKEN123"
    # ...but only the URL is ever persisted/returned back to the client.
    assert scan["target_reference"] == "https://github.com/example/private-repo.git"
    assert "ghp_secretTOKEN123" not in str(scan)


async def test_ai_endpoints_return_501_when_no_api_key_configured(client: AsyncClient) -> None:
    """No ANTHROPIC_API_KEY is set in the test environment, so `get_ai_analyzer`
    resolves to `NullAIAnalyzer` and every AI endpoint should surface that as
    a clean 501 - not a generic 500 or a silent empty response."""
    headers = await _register_and_login(client)
    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Demo Project"}, headers=headers
    )
    project_id = project_resp.json()["id"]

    scan_resp = await client.post(
        f"/api/v1/scans/upload?project_id={project_id}",
        headers=headers,
        files={"file": ("vulnerable.py", b"eval(user_input)\n", "text/x-python")},
    )
    scan = scan_resp.json()

    findings_resp = await client.get(f"/api/v1/findings?project_id={project_id}", headers=headers)
    finding_id = findings_resp.json()[0]["id"]

    explain_resp = await client.post(f"/api/v1/ai/findings/{finding_id}/explain", headers=headers)
    assert explain_resp.status_code == 501

    fix_resp = await client.post(f"/api/v1/ai/findings/{finding_id}/suggest-fix", headers=headers)
    assert fix_resp.status_code == 501

    summarize_resp = await client.post(f"/api/v1/ai/scans/{scan['id']}/summarize", headers=headers)
    assert summarize_resp.status_code == 501


async def test_ai_endpoint_requires_ownership_of_the_finding(client: AsyncClient) -> None:
    owner_headers = await _register_and_login(client, "owner@example.com")
    other_headers = await _register_and_login(client, "other@example.com")

    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Demo Project"}, headers=owner_headers
    )
    project_id = project_resp.json()["id"]
    await client.post(
        f"/api/v1/scans/upload?project_id={project_id}",
        headers=owner_headers,
        files={"file": ("vulnerable.py", b"eval(user_input)\n", "text/x-python")},
    )
    findings_resp = await client.get(
        f"/api/v1/findings?project_id={project_id}", headers=owner_headers
    )
    finding_id = findings_resp.json()[0]["id"]

    resp = await client.post(f"/api/v1/ai/findings/{finding_id}/explain", headers=other_headers)
    assert resp.status_code == 403


async def test_owner_can_add_collaborator_and_editor_can_then_scan(client: AsyncClient) -> None:
    owner_headers = await _register_and_login(client, "owner@example.com")
    await _register_and_login(client, "editor@example.com")

    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Shared Project"}, headers=owner_headers
    )
    project_id = project_resp.json()["id"]

    add_resp = await client.post(
        f"/api/v1/projects/{project_id}/collaborators",
        json={"email": "editor@example.com", "role": "editor"},
        headers=owner_headers,
    )
    assert add_resp.status_code == 201
    assert add_resp.json()["role"] == "editor"

    list_resp = await client.get(
        f"/api/v1/projects/{project_id}/collaborators", headers=owner_headers
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["email"] == "editor@example.com"

    # The editor can now see the project in their own list...
    editor_headers = await _register_and_login(client, "editor@example.com")
    editor_projects = await client.get("/api/v1/projects", headers=editor_headers)
    assert [p["id"] for p in editor_projects.json()] == [project_id]

    # ...and run a scan on it.
    scan_resp = await client.post(
        f"/api/v1/scans/upload?project_id={project_id}",
        headers=editor_headers,
        files={"file": ("vulnerable.py", b"eval(x)\n", "text/x-python")},
    )
    assert scan_resp.status_code == 201


async def test_viewer_cannot_run_scans_but_can_view(client: AsyncClient) -> None:
    owner_headers = await _register_and_login(client, "owner@example.com")
    await _register_and_login(client, "viewer@example.com")

    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Shared Project"}, headers=owner_headers
    )
    project_id = project_resp.json()["id"]

    await client.post(
        f"/api/v1/projects/{project_id}/collaborators",
        json={"email": "viewer@example.com", "role": "viewer"},
        headers=owner_headers,
    )

    viewer_headers = await _register_and_login(client, "viewer@example.com")

    get_resp = await client.get(f"/api/v1/projects/{project_id}", headers=viewer_headers)
    assert get_resp.status_code == 200

    scan_resp = await client.post(
        f"/api/v1/scans/upload?project_id={project_id}",
        headers=viewer_headers,
        files={"file": ("vulnerable.py", b"eval(x)\n", "text/x-python")},
    )
    assert scan_resp.status_code == 403


async def test_non_owner_cannot_manage_collaborators(client: AsyncClient) -> None:
    owner_headers = await _register_and_login(client, "owner@example.com")
    await _register_and_login(client, "editor@example.com")
    await _register_and_login(client, "third@example.com")

    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Shared Project"}, headers=owner_headers
    )
    project_id = project_resp.json()["id"]
    await client.post(
        f"/api/v1/projects/{project_id}/collaborators",
        json={"email": "editor@example.com", "role": "editor"},
        headers=owner_headers,
    )

    editor_headers = await _register_and_login(client, "editor@example.com")
    resp = await client.post(
        f"/api/v1/projects/{project_id}/collaborators",
        json={"email": "third@example.com", "role": "viewer"},
        headers=editor_headers,
    )
    assert resp.status_code == 403


async def test_owner_can_update_role_and_remove_collaborator(client: AsyncClient) -> None:
    owner_headers = await _register_and_login(client, "owner@example.com")
    await _register_and_login(client, "teammate@example.com")

    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Shared Project"}, headers=owner_headers
    )
    project_id = project_resp.json()["id"]
    add_resp = await client.post(
        f"/api/v1/projects/{project_id}/collaborators",
        json={"email": "teammate@example.com", "role": "viewer"},
        headers=owner_headers,
    )
    user_id = add_resp.json()["user_id"]

    patch_resp = await client.patch(
        f"/api/v1/projects/{project_id}/collaborators/{user_id}",
        json={"role": "editor"},
        headers=owner_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["role"] == "editor"

    delete_resp = await client.delete(
        f"/api/v1/projects/{project_id}/collaborators/{user_id}", headers=owner_headers
    )
    assert delete_resp.status_code == 204

    list_resp = await client.get(
        f"/api/v1/projects/{project_id}/collaborators", headers=owner_headers
    )
    assert list_resp.json() == []


async def test_upload_rejects_disallowed_extension(client: AsyncClient) -> None:
    headers = await _register_and_login(client)
    project_resp = await client.post(
        "/api/v1/projects", json={"name": "Demo Project"}, headers=headers
    )
    project_id = project_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/scans/upload?project_id={project_id}",
        headers=headers,
        files={"file": ("malware.exe", b"MZ", "application/octet-stream")},
    )
    assert resp.status_code == 400
