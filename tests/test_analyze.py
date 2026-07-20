"""Integrated tests for `maf-migrate analyze`.

Drives the CLI on fixture projects and asserts on observed outputs:
JSON content, detected generation, construct names and file:line locations.
No mocking of internal modules.
"""
import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "mini_projects"
GUIDE = Path(__file__).parent / "fixtures" / "guide"


def _analyze(path: Path) -> dict:
    """Run `maf-migrate analyze --json <path>` and return parsed JSON stdout."""
    result = subprocess.run(
        ["maf-migrate", "analyze", "--json", str(path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"analyze exited {result.returncode}: {result.stderr}"
    return json.loads(result.stdout)


def test_analyze_v04_single_detects_generation():
    data = _analyze(FIXTURES / "v04_single")
    assert data["generation"] == "0.4"


def test_analyze_v04_single_finds_imports():
    data = _analyze(FIXTURES / "v04_single")
    names = {c["name"] for c in data["constructs"]}
    assert "AssistantAgent" in names
    assert "OpenAIChatCompletionClient" in names


def test_analyze_v04_single_records_file_and_line():
    data = _analyze(FIXTURES / "v04_single")
    entries = {c["name"]: c for c in data["constructs"]}
    aa = entries["AssistantAgent"]
    assert aa["file"].endswith("main.py")
    assert isinstance(aa["line"], int) and aa["line"] > 0
    assert aa["module"] == "autogen_agentchat.agents"
    assert aa["kind"] == "import"


def test_analyze_v02_single_detects_generation():
    data = _analyze(FIXTURES / "v02_single")
    assert data["generation"] == "0.2"


def test_analyze_v02_single_finds_imports():
    data = _analyze(FIXTURES / "v02_single")
    names = {c["name"] for c in data["constructs"]}
    assert "AssistantAgent" in names
    assert "UserProxyAgent" in names


def test_analyze_mixed_detects_generation():
    data = _analyze(FIXTURES / "mixed")
    assert data["generation"] == "mixed"


def test_analyze_mixed_finds_both_generations():
    data = _analyze(FIXTURES / "mixed")
    modules = {c["module"] for c in data["constructs"]}
    assert any(m.startswith("autogen_agentchat") for m in modules), "no v0.4 module found"
    assert any(m in ("autogen", "pyautogen") for m in modules), "no v0.2 module found"


def test_analyze_files_scanned_count():
    data = _analyze(FIXTURES / "v04_single")
    assert data["files_scanned"] == 1


def test_analyze_guide_fixture_model_client():
    """Guide fixture: model_client_openai — v0.4 imports detected."""
    data = _analyze(GUIDE / "model_client_openai")
    assert data["generation"] == "0.4"
    names = {c["name"] for c in data["constructs"]}
    assert "OpenAIChatCompletionClient" in names
    assert "AzureOpenAIChatCompletionClient" in names


def test_analyze_outputs_valid_json_structure():
    data = _analyze(FIXTURES / "v04_single")
    assert "generation" in data
    assert "files_scanned" in data
    assert "constructs" in data
    assert isinstance(data["constructs"], list)
    for c in data["constructs"]:
        assert {"file", "line", "name", "module", "kind"} <= c.keys()
