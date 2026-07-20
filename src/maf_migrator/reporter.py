"""Human-readable migration report generator.

Takes scan output (from scanner.scan()) + mappings.yaml, and produces a
plain-text / Markdown report written for a stressed engineer, not a parser.
"""
from __future__ import annotations

import importlib.resources
from collections import Counter
from pathlib import Path
from typing import Optional

import yaml

_EFFORT = {
    "auto": "low — mechanical rename",
    "partial": "medium — config/param changes needed",
    "manual": "high — pattern rewrite required",
    "unknown": "unknown — not in mapping database",
}

_STATUS_LABEL = {
    "auto": "✓ AUTO",
    "partial": "~ PARTIAL",
    "manual": "✗ MANUAL",
    "unknown": "? UNKNOWN",
}


def _load_mappings() -> list[dict]:
    try:
        ref = importlib.resources.files("maf_migrator").joinpath("mappings.yaml")
        text = ref.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError):
        text = (Path(__file__).parent / "mappings.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text) or []


def _lookup(name: str, module: str, mappings: list[dict]) -> Optional[dict]:
    """Return the best mapping entry for (name, module), or None."""
    for m in mappings:
        if m.get("name") == name and m.get("module") == module:
            return m
    return None


def generate_report(scan: dict, project_path: Path) -> str:
    """Generate a human-readable migration report from *scan* result dict."""
    mappings = _load_mappings()

    # Deduplicate constructs by (name, module) and count occurrences
    counts: Counter[tuple[str, str]] = Counter()
    for c in scan.get("constructs", []):
        counts[(c["name"], c["module"])] += 1

    # Annotate each unique construct with its mapping
    annotated: list[dict] = []
    for (name, module), count in sorted(counts.items(), key=lambda x: (-x[1], x[0][0], x[0][1])):
        entry = _lookup(name, module, mappings)
        annotated.append(
            {
                "name": name,
                "module": module,
                "count": count,
                "status": entry["status"] if entry else "unknown",
                "maf_equivalent": entry.get("maf_equivalent") if entry else None,
                "maf_module": entry.get("maf_module") if entry else None,
                "notes": (entry.get("notes") or "").strip() if entry else None,
                "ag2_note": (entry.get("ag2_note") or "").strip() if entry else None,
            }
        )

    by_status: dict[str, list[dict]] = {s: [] for s in ("auto", "partial", "manual", "unknown")}
    for a in annotated:
        by_status[a["status"]].append(a)

    total = len(annotated)
    generation = scan.get("generation", "unknown")
    files_scanned = scan.get("files_scanned", 0)
    dirname = project_path.resolve().name

    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append(f"# MAF Migration Report — {dirname}")
    lines.append("")
    lines.append(f"Files scanned: {files_scanned}  |  AutoGen generation: {generation}")
    lines.append("")

    # ── Summary ───────────────────────────────────────────────────────────────
    lines.append("## SUMMARY")
    lines.append("")
    lines.append(f"  Total unique constructs: {total}")
    lines.append("")

    for status in ("auto", "partial", "manual", "unknown"):
        n = len(by_status[status])
        label = _STATUS_LABEL[status]
        effort = _EFFORT[status]
        lines.append(f"  {label:<12}  {n:>3}  construct{'s' if n != 1 else ''}  ({effort})")

    lines.append("")

    if total == 0:
        lines.append("No AutoGen constructs found. Nothing to migrate.")
        lines.append("")
        return "\n".join(lines)

    # ── Construct details by status ───────────────────────────────────────────
    lines.append("## CONSTRUCTS")
    lines.append("")

    section_titles = {
        "auto": "✓ AUTO — low effort (mechanical rename)",
        "partial": "~ PARTIAL — medium effort (config/param changes needed)",
        "manual": "✗ MANUAL — high effort (pattern rewrite required)",
        "unknown": "? UNKNOWN — not in mapping database",
    }

    for status in ("auto", "partial", "manual", "unknown"):
        items = by_status[status]
        if not items:
            continue

        lines.append(f"### {section_titles[status]}")
        lines.append("")

        for item in items:
            count_tag = f"({item['count']}×)" if item["count"] > 1 else ""
            if item["maf_equivalent"] and item["maf_module"]:
                arrow = f"→  {item['maf_equivalent']} ({item['maf_module']})"
            elif item["maf_equivalent"]:
                arrow = f"→  {item['maf_equivalent']}"
            else:
                arrow = "→  (no direct MAF equivalent)"

            lines.append(f"  {item['name']:<40}  {count_tag}")
            lines.append(f"    from {item['module']}")
            lines.append(f"    {arrow}")
            if item["notes"]:
                # Wrap note lines at 80 chars
                note_words = item["notes"].split()
                note_lines: list[str] = []
                current = "    Note: "
                for word in note_words:
                    if len(current) + len(word) + 1 > 82:
                        note_lines.append(current.rstrip())
                        current = "          " + word + " "
                    else:
                        current += word + " "
                if current.strip():
                    note_lines.append(current.rstrip())
                lines.extend(note_lines)
            lines.append("")

    # ── Destination note ──────────────────────────────────────────────────────
    lines.append("## DESTINATION NOTE")
    lines.append("")

    ag2_constructs = [a for a in annotated if a.get("ag2_note")]
    has_legacy = generation in ("0.2", "mixed") or any(
        "autogen" == c["module"] or c["module"].startswith("pyautogen")
        or (c["module"] == "autogen" and not c["module"].startswith("autogen_"))
        for c in annotated
    )

    lines.append(
        "This report targets Microsoft Agent Framework (MAF) as the migration destination."
    )
    lines.append("")

    if ag2_constructs or has_legacy:
        lines.append(
            "AG2 alternative: some constructs in this project are marked AG2-compatible —"
        )
        lines.append(
            "AG2 preserves more of the original AutoGen API surface and may be a lower-effort"
        )
        lines.append(
            "target if your team is not committed to MAF. See construct notes above (ag2_note)."
        )
        lines.append("")

    lines.append(
        "Run `maf-migrate run <path>` to apply AUTO transforms automatically (pro tier)."
    )
    lines.append("")

    return "\n".join(lines)
