"""Integrated tests for `maf-migrate analyze` human-readable report output.

Drives the CLI on two fixture projects, compares output to golden snapshots
under tests/fixtures/report_snapshots/. Golden files are the source of truth —
regenerate them with --json-snapshot to update after intentional format changes.

No mocking of internal modules.
"""
import subprocess
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "mini_projects"
SNAPSHOTS = Path(__file__).parent / "fixtures" / "report_snapshots"


def _analyze_report(path: Path, output_file: Path | None = None) -> str:
    """Run `maf-migrate analyze <path>` and return stdout."""
    cmd = ["maf-migrate", "analyze", str(path)]
    if output_file:
        cmd += ["--output", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"analyze exited {result.returncode}:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return result.stdout


def _analyze_json(path: Path) -> str:
    """Run `maf-migrate analyze --json <path>` and return stdout."""
    result = subprocess.run(
        ["maf-migrate", "analyze", "--json", str(path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"analyze --json exited {result.returncode}: {result.stderr}"
    return result.stdout


# ── Golden-file snapshot tests ─────────────────────────────────────────────────

def test_report_v04_single_matches_snapshot():
    """Report for v04_single matches stored golden file."""
    report = _analyze_report(FIXTURES / "v04_single")
    snapshot_path = SNAPSHOTS / "v04_single.txt"
    assert snapshot_path.exists(), (
        f"Golden snapshot missing: {snapshot_path}\n"
        "Run `maf-migrate analyze tests/fixtures/mini_projects/v04_single "
        "> tests/fixtures/report_snapshots/v04_single.txt` to create it."
    )
    expected = snapshot_path.read_text()
    assert report == expected, (
        "Report output does not match golden snapshot.\n"
        "If the format changed intentionally, update the snapshot file."
    )


def test_report_mixed_matches_snapshot():
    """Report for mixed (v0.2 + v0.4) project matches stored golden file."""
    report = _analyze_report(FIXTURES / "mixed")
    snapshot_path = SNAPSHOTS / "mixed.txt"
    assert snapshot_path.exists(), (
        f"Golden snapshot missing: {snapshot_path}\n"
        "Run `maf-migrate analyze tests/fixtures/mini_projects/mixed "
        "> tests/fixtures/report_snapshots/mixed.txt` to create it."
    )
    expected = snapshot_path.read_text()
    assert report == expected, (
        "Report output does not match golden snapshot.\n"
        "If the format changed intentionally, update the snapshot file."
    )


# ── Structural content tests ───────────────────────────────────────────────────

def test_report_v04_contains_summary_header():
    report = _analyze_report(FIXTURES / "v04_single")
    assert "SUMMARY" in report


def test_report_v04_shows_generation():
    report = _analyze_report(FIXTURES / "v04_single")
    assert "0.4" in report


def test_report_v04_lists_auto_constructs():
    report = _analyze_report(FIXTURES / "v04_single")
    assert "AssistantAgent" in report
    assert "OpenAIChatCompletionClient" in report


def test_report_v04_shows_auto_status():
    report = _analyze_report(FIXTURES / "v04_single")
    assert "AUTO" in report or "auto" in report.lower()


def test_report_mixed_shows_manual_status():
    """Mixed project has ConversableAgent (manual) — report must surface it."""
    report = _analyze_report(FIXTURES / "mixed")
    assert "ConversableAgent" in report
    assert "MANUAL" in report or "manual" in report.lower()


def test_report_mixed_shows_ag2_note():
    """Mixed project has legacy 0.2 agents — AG2 destination note must appear."""
    report = _analyze_report(FIXTURES / "mixed")
    assert "AG2" in report or "ag2" in report.lower()


def test_report_has_destination_note_section():
    report = _analyze_report(FIXTURES / "mixed")
    assert "DESTINATION" in report or "destination" in report.lower()


# ── --output flag ──────────────────────────────────────────────────────────────

def test_report_output_flag_writes_file(tmp_path):
    """--output writes the report to a file; stdout is empty (or a status line)."""
    out = tmp_path / "report.md"
    stdout = _analyze_report(FIXTURES / "v04_single", output_file=out)
    assert out.exists(), "--output flag did not create the file"
    content = out.read_text()
    assert "AssistantAgent" in content, "Report file does not contain expected construct"
    assert "SUMMARY" in content


def test_report_output_file_is_markdown(tmp_path):
    """--output file should start with a Markdown heading."""
    out = tmp_path / "report.md"
    _analyze_report(FIXTURES / "v04_single", output_file=out)
    content = out.read_text()
    assert content.lstrip().startswith("#"), "Report file does not start with a Markdown heading"


# ── --json backward-compat ────────────────────────────────────────────────────

def test_json_flag_still_emits_json():
    """--json flag preserves machine-readable output for downstream tooling."""
    import json
    raw = _analyze_json(FIXTURES / "v04_single")
    data = json.loads(raw)
    assert "generation" in data
    assert "constructs" in data
