"""Integrated tests for `maf-migrate inventory`.

Drives the CLI on two fixture projects and asserts on aggregated output:
repo count, construct frequencies, markdown rendering.  No mocking of internal
modules; no network calls.
"""
import json
import subprocess
import tempfile
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "mini_projects"


def _inventory(*paths: Path) -> dict:
    """Run `maf-migrate inventory <paths...>` and return parsed JSON stdout."""
    result = subprocess.run(
        ["maf-migrate", "inventory"] + [str(p) for p in paths],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"inventory exited {result.returncode}: {result.stderr}"
    return json.loads(result.stdout)


def test_inventory_repos_analyzed_count():
    data = _inventory(FIXTURES / "v04_single", FIXTURES / "mixed")
    assert data["repos_analyzed"] == 2


def test_inventory_returns_constructs_list():
    data = _inventory(FIXTURES / "v04_single", FIXTURES / "mixed")
    assert "constructs" in data
    assert isinstance(data["constructs"], list)
    assert len(data["constructs"]) > 0


def test_inventory_construct_has_required_fields():
    data = _inventory(FIXTURES / "v04_single", FIXTURES / "mixed")
    for c in data["constructs"]:
        assert {"name", "module", "generation", "repo_count"} <= c.keys()


def test_inventory_cross_repo_frequency():
    """AssistantAgent from autogen_agentchat.agents appears in both v04_single and mixed."""
    data = _inventory(FIXTURES / "v04_single", FIXTURES / "mixed")
    matching = [
        c for c in data["constructs"]
        if c["name"] == "AssistantAgent" and c["module"] == "autogen_agentchat.agents"
    ]
    assert len(matching) == 1, "Expected exactly one AssistantAgent entry from autogen_agentchat.agents"
    assert matching[0]["repo_count"] == 2


def test_inventory_single_repo_construct_frequency():
    """OpenAIChatCompletionClient only appears in v04_single, not in mixed."""
    data = _inventory(FIXTURES / "v04_single", FIXTURES / "mixed")
    matching = [c for c in data["constructs"] if c["name"] == "OpenAIChatCompletionClient"]
    assert len(matching) == 1
    assert matching[0]["repo_count"] == 1


def test_inventory_sorted_by_frequency_descending():
    data = _inventory(FIXTURES / "v04_single", FIXTURES / "mixed")
    counts = [c["repo_count"] for c in data["constructs"]]
    assert counts == sorted(counts, reverse=True)


def test_inventory_generation_tagged_correctly():
    data = _inventory(FIXTURES / "v04_single", FIXTURES / "mixed")
    for c in data["constructs"]:
        if "autogen_agentchat" in c["module"] or "autogen_ext" in c["module"]:
            assert c["generation"] == "0.4", f"{c['module']} should be tagged 0.4"
        if c["module"] in ("autogen", "pyautogen"):
            assert c["generation"] == "0.2", f"{c['module']} should be tagged 0.2"


def test_inventory_output_flag_writes_markdown():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
        tmp_path = tmp.name
    result = subprocess.run(
        ["maf-migrate", "inventory",
         str(FIXTURES / "v04_single"),
         str(FIXTURES / "mixed"),
         "--output", tmp_path],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    content = Path(tmp_path).read_text()
    assert "# Corpus construct-frequency inventory" in content
    assert "AssistantAgent" in content
    assert "| Rank |" in content


def test_inventory_output_flag_markdown_has_repo_count():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
        tmp_path = tmp.name
    subprocess.run(
        ["maf-migrate", "inventory",
         str(FIXTURES / "v04_single"),
         str(FIXTURES / "mixed"),
         "--output", tmp_path],
        capture_output=True, text=True, check=True,
    )
    content = Path(tmp_path).read_text()
    # The highest-frequency construct (repo_count=2) should appear with a "2" in its row
    lines = [l for l in content.splitlines() if "AssistantAgent" in l and "autogen_agentchat.agents" in l]
    assert lines, "Expected a markdown row for AssistantAgent from autogen_agentchat.agents"
    assert "| 2 |" in lines[0], f"Expected repo_count=2 in row: {lines[0]}"
