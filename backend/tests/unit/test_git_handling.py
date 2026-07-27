import git
import pytest

from app.core.exceptions import UnsupportedFileError
from app.utils.git_handling import clone_repository


def test_clone_repository_rejects_non_http_scheme(tmp_path) -> None:
    with pytest.raises(UnsupportedFileError):
        clone_repository("file:///etc/passwd", tmp_path / "workspace")


def test_clone_repository_rejects_ssh_scheme(tmp_path) -> None:
    with pytest.raises(UnsupportedFileError):
        clone_repository("git@github.com:owner/repo.git", tmp_path / "workspace")


def test_clone_repository_rejects_leading_dash_argument_injection(tmp_path) -> None:
    with pytest.raises(UnsupportedFileError):
        clone_repository("-upload-pack=evil", tmp_path / "workspace")


def test_clone_repository_calls_git_clone_from_with_shallow_depth(tmp_path, monkeypatch) -> None:
    captured: dict = {}

    def fake_clone_from(url, destination, depth, multi_options, allow_unsafe_options):
        captured["url"] = url
        captured["destination"] = destination
        captured["depth"] = depth
        captured["multi_options"] = multi_options
        captured["allow_unsafe_options"] = allow_unsafe_options

    monkeypatch.setattr(git.Repo, "clone_from", staticmethod(fake_clone_from))

    destination = tmp_path / "workspace"
    result = clone_repository("https://github.com/example/repo.git", destination)

    assert result == destination
    assert captured["url"] == "https://github.com/example/repo.git"
    assert captured["depth"] == 1
    assert captured["multi_options"] == ["--no-tags"]
    assert captured["allow_unsafe_options"] is False


def test_clone_repository_wraps_git_command_error(tmp_path, monkeypatch) -> None:
    def failing_clone_from(*args, **kwargs):
        raise git.GitCommandError("clone", 128, stderr="repository not found")

    monkeypatch.setattr(git.Repo, "clone_from", staticmethod(failing_clone_from))

    with pytest.raises(UnsupportedFileError):
        clone_repository("https://github.com/example/does-not-exist.git", tmp_path / "workspace")


def test_clone_repository_with_token_sets_auth_header_via_config(tmp_path, monkeypatch) -> None:
    captured: dict = {}

    def fake_clone_from(url, destination, depth, multi_options, allow_unsafe_options):
        captured["multi_options"] = multi_options
        captured["allow_unsafe_options"] = allow_unsafe_options

    monkeypatch.setattr(git.Repo, "clone_from", staticmethod(fake_clone_from))

    clone_repository(
        "https://github.com/example/private-repo.git", tmp_path / "workspace", "ghp_secretTOKEN123"
    )

    assert captured["allow_unsafe_options"] is True
    assert "-c" in captured["multi_options"]
    header_arg = captured["multi_options"][captured["multi_options"].index("-c") + 1]
    assert header_arg == "http.extraheader=AUTHORIZATION: bearer ghp_secretTOKEN123"
    assert "--no-tags" in captured["multi_options"]


def test_clone_repository_rejects_token_with_invalid_characters(tmp_path) -> None:
    with pytest.raises(UnsupportedFileError):
        clone_repository(
            "https://github.com/example/repo.git",
            tmp_path / "workspace",
            "token-with-a-newline\nAUTHORIZATION: bearer evil",
        )


def test_clone_repository_never_persists_or_leaks_token_on_failure(tmp_path, monkeypatch) -> None:
    secret = "ghp_secretTOKEN123"

    def failing_clone_from(*args, **kwargs):
        raise git.GitCommandError("clone", 128, stderr=f"fatal: header value was {secret}")

    monkeypatch.setattr(git.Repo, "clone_from", staticmethod(failing_clone_from))

    with pytest.raises(UnsupportedFileError) as exc_info:
        clone_repository("https://github.com/example/repo.git", tmp_path / "workspace", secret)

    assert secret not in str(exc_info.value)
