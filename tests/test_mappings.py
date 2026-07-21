"""Integrated tests for mappings.yaml knowledge base.

Validates schema correctness and that every construct seen in the guide
fixtures has a mapping entry.
"""
import yaml
from pathlib import Path

from maf_migrator.scanner import scan

MAPPINGS_PATH = Path(__file__).parent.parent / "src" / "maf_migrator" / "mappings.yaml"
GUIDE_FIXTURES = Path(__file__).parent / "fixtures" / "guide"

VALID_STATUSES = {"auto", "partial", "manual", "unknown"}
REQUIRED_FIELDS = {"name", "module", "generation", "status"}
OPTIONAL_FIELDS = {"maf_equivalent", "maf_module", "guide_link", "ag2_note", "notes"}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS


def _load() -> list[dict]:
    return yaml.safe_load(MAPPINGS_PATH.read_text())


def test_mappings_file_exists():
    assert MAPPINGS_PATH.exists(), f"mappings.yaml not found at {MAPPINGS_PATH}"


def test_mappings_is_list():
    data = _load()
    assert isinstance(data, list)
    assert len(data) > 0


def test_mappings_required_fields():
    data = _load()
    for i, entry in enumerate(data):
        for field in REQUIRED_FIELDS:
            assert field in entry, f"Entry {i} missing required field '{field}': {entry}"


def test_mappings_no_unknown_fields():
    data = _load()
    for i, entry in enumerate(data):
        for field in entry:
            assert field in ALL_FIELDS, f"Entry {i} has unrecognised field '{field}'"


def test_mappings_status_values():
    data = _load()
    for i, entry in enumerate(data):
        assert entry["status"] in VALID_STATUSES, (
            f"Entry {i} has invalid status '{entry['status']}'; must be one of {VALID_STATUSES}"
        )


def test_mappings_generation_values():
    data = _load()
    for i, entry in enumerate(data):
        assert entry["generation"] in {"0.4", "0.2"}, (
            f"Entry {i} has invalid generation '{entry['generation']}'"
        )


def test_guide_constructs_covered():
    """Every AutoGen construct imported in guide before.py files has an entry."""
    data = _load()
    covered = {(e["name"], e["module"]) for e in data}

    inventory = scan(GUIDE_FIXTURES)
    guide_constructs = [
        (c["name"], c["module"])
        for c in inventory["constructs"]
        if "before.py" in c["file"]
    ]

    missing = [c for c in guide_constructs if c not in covered]
    assert not missing, f"Guide constructs missing from mappings.yaml: {missing}"


def test_auto_mappings_have_maf_equivalent():
    """Entries with status='auto' must declare a maf_equivalent."""
    data = _load()
    for i, entry in enumerate(data):
        if entry["status"] == "auto":
            assert entry.get("maf_equivalent"), (
                f"Entry {i} has status='auto' but no maf_equivalent: {entry}"
            )


# ── 1.5a acceptance test ──────────────────────────────────────────────────────

PRIORITY_CONSTRUCTS_1_5A = [
    # (name, module) — these were all UNKNOWN at GATE 1.5 and must be classified after 1.5a
    ("RoundRobinGroupChat", "autogen_agentchat.teams"),
    ("SelectorGroupChat", "autogen_agentchat.teams"),
    ("MaxMessageTermination", "autogen_agentchat.conditions"),
    ("TextMentionTermination", "autogen_agentchat.conditions"),
    ("Console", "autogen_agentchat.ui"),
    ("ChatCompletionClient", "autogen_core.models"),
    ("UserMessage", "autogen_core.models"),
    ("AssistantMessage", "autogen_core.models"),
    ("LLMMessage", "autogen_core.models"),
    ("BufferedChatCompletionContext", "autogen_core.model_context"),
]


def test_1_5a_priority_constructs_classified():
    """All priority-1.5a constructs must have a non-unknown status with a reason (notes field)."""
    data = _load()
    index = {(e["name"], e["module"]): e for e in data}

    not_classified = []
    for name, module in PRIORITY_CONSTRUCTS_1_5A:
        entry = index.get((name, module))
        if entry is None:
            not_classified.append(f"MISSING: ({name}, {module})")
        elif entry["status"] == "unknown":
            not_classified.append(f"STILL UNKNOWN: ({name}, {module})")

    assert not not_classified, (
        "These 1.5a priority constructs are not yet classified:\n"
        + "\n".join(not_classified)
    )


def test_1_5a_multiagent_fixture_constructs_in_mappings():
    """All constructs from the v04_multiagent fixture must appear in mappings.yaml."""
    data = _load()
    covered = {(e["name"], e["module"]) for e in data}

    fixture = Path(__file__).parent / "fixtures" / "mini_projects" / "v04_multiagent"
    inventory = scan(fixture)
    constructs = [(c["name"], c["module"]) for c in inventory["constructs"]]

    missing = [c for c in constructs if c not in covered]
    assert not missing, f"v04_multiagent fixture constructs missing from mappings.yaml: {missing}"
