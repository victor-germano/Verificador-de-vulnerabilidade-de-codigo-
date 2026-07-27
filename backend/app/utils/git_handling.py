import re
from pathlib import Path

import git

from app.core.exceptions import UnsupportedFileError

_ALLOWED_SCHEMES = ("https://", "http://")

# Deliberately restrictive: PATs from GitHub/GitLab/Bitbucket are all
# alphanumeric plus `_`/`-`/`.`/`:` (the last for `x-token-auth:<token>`
# style values). Rejecting anything else blocks header/config injection via
# the token value (e.g. embedded newlines or `=`) before it ever reaches
# the `git` subprocess.
_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_\-.:]+$")


def clone_repository(url: str, destination: Path, access_token: str | None = None) -> Path:
    """Shallow-clones a git repository into `destination` for scanning.

    Only `http(s)://` URLs are accepted - `file://`/SSH targets are
    rejected so the endpoint can't be used to read arbitrary local paths on
    the server (SSRF-adjacent risk), and a leading `-` is rejected so the
    URL can never be interpreted as a CLI flag by the underlying `git`
    binary (argument injection). Depth is capped at 1: we only need the
    current state of the code, not its history.

    For private repositories, pass `access_token` (a PAT). It is sent via
    an `http.extraheader` git config override scoped to this single clone
    - never embedded in the URL, so it's never written to `.git/config` or
    liable to be echoed back in a URL-based error message. The token is
    also never persisted (only the plain `url` is stored as
    `Scan.target_reference`) and is scrubbed from any exception raised
    here before it propagates.
    """
    if not url.startswith(_ALLOWED_SCHEMES) or url.lstrip().startswith("-"):
        raise UnsupportedFileError("Only http:// or https:// git URLs are supported.")

    multi_options = ["--no-tags"]
    if access_token is not None:
        if not _TOKEN_PATTERN.fullmatch(access_token):
            raise UnsupportedFileError("access_token has an invalid format.")
        multi_options = [
            "-c",
            f"http.extraheader=AUTHORIZATION: bearer {access_token}",
            *multi_options,
        ]

    destination.mkdir(parents=True, exist_ok=True)
    try:
        git.Repo.clone_from(
            url,
            destination,
            depth=1,
            multi_options=multi_options,
            allow_unsafe_options=access_token is not None,
        )
    except git.GitCommandError as exc:
        message = str(exc).replace(access_token, "***") if access_token else str(exc)
        raise UnsupportedFileError(f"Failed to clone repository: {message}") from exc

    return destination
