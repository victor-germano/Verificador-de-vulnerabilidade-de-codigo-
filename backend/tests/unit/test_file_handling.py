import io
import zipfile

import pytest
from fastapi import UploadFile

from app.core.exceptions import UnsupportedFileError
from app.utils.file_handling import extract_if_archive, save_upload


def _upload_file(filename: str, content: bytes) -> UploadFile:
    return UploadFile(file=io.BytesIO(content), filename=filename)


async def test_save_upload_writes_file_to_destination(tmp_path) -> None:
    upload = _upload_file("script.py", b"print('hi')")
    saved_path = await save_upload(upload, tmp_path)
    assert saved_path.read_bytes() == b"print('hi')"
    assert saved_path.parent == tmp_path


async def test_save_upload_rejects_disallowed_extension(tmp_path) -> None:
    upload = _upload_file("malware.exe", b"MZ")
    with pytest.raises(UnsupportedFileError):
        await save_upload(upload, tmp_path)


def test_extract_if_archive_returns_path_unchanged_for_non_zip(tmp_path) -> None:
    file_path = tmp_path / "script.py"
    file_path.write_text("x = 1")
    assert extract_if_archive(file_path) == file_path


def test_extract_if_archive_extracts_zip_contents(tmp_path) -> None:
    zip_path = tmp_path / "project.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("app.py", "eval(x)")

    extracted_dir = extract_if_archive(zip_path)

    assert extracted_dir.is_dir()
    assert (extracted_dir / "app.py").read_text() == "eval(x)"


def test_extract_if_archive_rejects_zip_slip(tmp_path) -> None:
    zip_path = tmp_path / "malicious.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("../../evil.py", "import os; os.system('rm -rf /')")

    with pytest.raises(UnsupportedFileError):
        extract_if_archive(zip_path)
