"""AutoGen API usage scanner.

Walks a directory tree, parses Python files with ast, and returns an inventory
of AutoGen constructs (imported names, per file:line, with generation tag).
"""
import ast
import json
from pathlib import Path

# Modules that indicate AutoGen v0.4
_V04_PREFIXES = (
    "autogen_agentchat",
    "autogen_core",
    "autogen_ext",
    "autogen_magentic_one",
)

# Modules that indicate AutoGen v0.2 / legacy
_V02_PREFIXES = (
    "autogen",
    "pyautogen",
)


def _classify_module(module: str) -> str | None:
    """Return '0.4', '0.2', or None if unrelated."""
    for prefix in _V04_PREFIXES:
        if module == prefix or module.startswith(prefix + "."):
            return "0.4"
    for prefix in _V02_PREFIXES:
        if module == prefix or module.startswith(prefix + "."):
            return "0.2"
    return None


def _scan_file(path: Path) -> list[dict]:
    """Return construct entries from a single Python file."""
    try:
        if not path.is_file():
            return []
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    entries = []

    for node in ast.walk(tree):
        # from <module> import <name>, <name>, ...
        if isinstance(node, ast.ImportFrom) and node.module:
            gen = _classify_module(node.module)
            if gen is not None:
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    entries.append(
                        {
                            "file": str(path),
                            "line": node.lineno,
                            "name": alias.name,
                            "module": node.module,
                            "kind": "import",
                        }
                    )
        # import <module> (bare import)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                gen = _classify_module(alias.name)
                if gen is not None:
                    name = alias.asname if alias.asname else alias.name
                    entries.append(
                        {
                            "file": str(path),
                            "line": node.lineno,
                            "name": name,
                            "module": alias.name,
                            "kind": "import",
                        }
                    )

    return entries


def scan(directory: Path) -> dict:
    """Scan *directory* for AutoGen usage and return a structured inventory."""
    py_files = sorted(directory.rglob("*.py"))
    all_entries: list[dict] = []

    for py_file in py_files:
        all_entries.extend(_scan_file(py_file))

    # Determine generation
    gens = {_classify_module(e["module"]) for e in all_entries if _classify_module(e["module"])}
    if len(gens) > 1:
        generation = "mixed"
    elif gens == {"0.4"}:
        generation = "0.4"
    elif gens == {"0.2"}:
        generation = "0.2"
    else:
        generation = "unknown"

    return {
        "generation": generation,
        "files_scanned": len(py_files),
        "constructs": all_entries,
    }


def scan_to_json(directory: Path) -> str:
    return json.dumps(scan(directory), indent=2)
