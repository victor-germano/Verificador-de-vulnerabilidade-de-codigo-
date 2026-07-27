import json

from app.cli import main


def test_cli_scans_file_and_prints_json_report(tmp_path, capsys) -> None:
    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\n", encoding="utf-8")

    exit_code = main([str(target)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["files_scanned"] == 1
    assert any(f["rule_id"] == "CODE001" for f in payload["findings"])
    assert "Security Score" in captured.err


def test_cli_writes_report_to_output_file(tmp_path) -> None:
    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\n", encoding="utf-8")
    output = tmp_path / "report.md"

    exit_code = main([str(target), "--format", "markdown", "--output", str(output)])

    assert exit_code == 0
    assert output.exists()
    assert "CODE001" in output.read_text(encoding="utf-8")


def test_cli_returns_2_for_missing_path(tmp_path) -> None:
    missing = tmp_path / "does-not-exist.py"
    assert main([str(missing)]) == 2


def test_cli_requires_output_for_pdf_format(tmp_path) -> None:
    target = tmp_path / "clean.py"
    target.write_text("x = 1\n", encoding="utf-8")
    assert main([str(target), "--format", "pdf"]) == 2


def test_cli_fail_on_returns_1_when_threshold_reached(tmp_path) -> None:
    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\n", encoding="utf-8")  # CODE001, critical

    assert main([str(target), "--fail-on", "critical", "--output", str(tmp_path / "r.json")]) == 1


def test_cli_fail_on_returns_0_when_threshold_not_reached(tmp_path) -> None:
    target = tmp_path / "clean.py"
    target.write_text("x = 1\n", encoding="utf-8")

    assert main([str(target), "--fail-on", "critical", "--output", str(tmp_path / "r.json")]) == 0


def test_cli_uses_directory_name_as_default_project_name(tmp_path) -> None:
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    output = tmp_path / "report.json"

    main([str(tmp_path), "--output", str(output)])

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["project_name"] == tmp_path.name
