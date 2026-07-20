"""Construct-frequency aggregator across multiple repos."""
from collections import defaultdict
from pathlib import Path

from .scanner import scan, _classify_module


def aggregate(directories: list[Path]) -> dict:
    """Scan each directory and return a cross-repo construct-frequency table."""
    # (name, module) -> set of repo paths (one entry per repo, deduplicated within)
    construct_repos: dict[tuple[str, str], set[str]] = defaultdict(set)
    repos_analyzed = 0

    for d in directories:
        result = scan(d)
        repo_key = str(d)
        repos_analyzed += 1

        seen: set[tuple[str, str]] = set()
        for c in result["constructs"]:
            key = (c["name"], c["module"])
            if key not in seen:
                construct_repos[key].add(repo_key)
                seen.add(key)

    rows = []
    for (name, module), repos in sorted(
        construct_repos.items(), key=lambda x: -len(x[1])
    ):
        gen = _classify_module(module) or "unknown"
        rows.append(
            {
                "name": name,
                "module": module,
                "generation": gen,
                "repo_count": len(repos),
            }
        )

    return {
        "repos_analyzed": repos_analyzed,
        "total_constructs": len(rows),
        "constructs": rows,
    }


def to_markdown(result: dict) -> str:
    """Render aggregation result as a Markdown table."""
    lines = [
        "# Corpus construct-frequency inventory",
        "",
        f"Repos analyzed: **{result['repos_analyzed']}** | Unique constructs: **{result['total_constructs']}**",
        "",
        "Sorted by frequency (number of repos importing each construct).",
        "This table sets the build order for Phase 2 transforms — highest-frequency constructs first.",
        "",
        "| Rank | Construct | Module | Generation | Repos |",
        "|------|-----------|--------|------------|-------|",
    ]
    for rank, c in enumerate(result["constructs"], 1):
        lines.append(
            f"| {rank} | `{c['name']}` | `{c['module']}` | {c['generation']} | {c['repo_count']} |"
        )
    return "\n".join(lines) + "\n"
