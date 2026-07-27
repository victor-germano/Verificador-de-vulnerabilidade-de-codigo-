import shutil
import uuid
import zipfile
from pathlib import Path

from fastapi import UploadFile

from app.config import get_settings
from app.core.exceptions import UnsupportedFileError

settings = get_settings()


async def save_upload(upload: UploadFile, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename or "upload").suffix
    if suffix not in settings.allowed_upload_extensions:
        raise UnsupportedFileError(f"File extension '{suffix}' is not supported.")

    target_path = destination_dir / (upload.filename or f"{uuid.uuid4()}{suffix}")
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return target_path


def extract_if_archive(path: Path) -> Path:
    """If `path` is a `.zip`, extracts it next to itself and returns the
    extraction directory; otherwise returns `path` unchanged.

    Validates every member path stays inside the extraction directory
    before extracting - a zip crafted with `../` entries ("zip slip") could
    otherwise write outside of it. Being a security tool ourselves, we
    don't get to skip this check.
    """
    if path.suffix != ".zip":
        return path

    extract_dir = path.with_suffix("")
    extract_dir.mkdir(parents=True, exist_ok=True)
    resolved_root = extract_dir.resolve()

    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            member_path = (extract_dir / member.filename).resolve()
            if not str(member_path).startswith(str(resolved_root)):
                raise UnsupportedFileError("Zip archive contains an invalid path (zip slip).")
        archive.extractall(extract_dir)

    return extract_dir


def new_upload_workspace() -> Path:
    workspace = Path(settings.upload_dir) / str(uuid.uuid4())
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
