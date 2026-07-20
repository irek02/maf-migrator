#!/usr/bin/env python3
"""Corpus runner: clone and manage AutoGen benchmark repos.

Usage:
  python scripts/corpus.py            # clone all repos to corpus/ (checks out pinned commit)
  python scripts/corpus.py --dry-run  # validate manifest, no cloning
  python scripts/corpus.py --repin    # shallow-clone to HEAD, capture real SHAs, update corpus.yaml
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
CORPUS_YAML = ROOT / "corpus.yaml"
CORPUS_DIR = ROOT / "corpus"

REQUIRED_FIELDS = {"name", "url", "commit", "license", "generation"}
VALID_GENERATIONS = {"v0.4", "v0.2", "mixed"}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def load_manifest():
    with open(CORPUS_YAML) as f:
        return yaml.safe_load(f)


def validate_manifest(manifest):
    """Return list of schema error strings; empty list means valid."""
    errors = []
    repos = manifest.get("repos")
    if not isinstance(repos, list):
        return ["'repos' key missing or not a list"]
    for i, repo in enumerate(repos):
        label = repo.get("name", f"[{i}]")
        missing = REQUIRED_FIELDS - set(repo.keys())
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
        gen = repo.get("generation")
        if gen not in VALID_GENERATIONS:
            errors.append(f"{label}: invalid generation {gen!r}; must be one of {sorted(VALID_GENERATIONS)}")
        commit = repo.get("commit", "")
        if not COMMIT_RE.match(commit):
            errors.append(f"{label}: invalid commit {commit!r}; must be a 40-char lowercase hex SHA")
        url = repo.get("url", "")
        if not url.startswith("https://github.com/"):
            errors.append(f"{label}: url must start with https://github.com/: {url!r}")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Clone and manage AutoGen corpus repos.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate manifest and print what would be cloned; no network calls.",
    )
    parser.add_argument(
        "--repin",
        action="store_true",
        help="Shallow-clone each repo to HEAD, capture real SHAs, update corpus.yaml.",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    errors = validate_manifest(manifest)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    repos = manifest["repos"]
    print(f"Corpus: {len(repos)} repos")

    if args.dry_run:
        for r in repos:
            print(f"  [{r['generation']}] {r['name']} ({r['license']}) -> corpus/{r['name']}")
        print("Dry run OK — no cloning performed.")
        return

    CORPUS_DIR.mkdir(exist_ok=True)

    if args.repin:
        updated = False
        for r in repos:
            dest = CORPUS_DIR / r["name"]
            if dest.exists():
                print(f"  already cloned: {r['name']} — re-reading HEAD SHA")
            else:
                print(f"  shallow-cloning {r['name']} ...")
                result = subprocess.run(
                    ["git", "clone", "--depth=1", "--filter=blob:none", r["url"], str(dest)],
                    capture_output=True, text=True,
                )
                if result.returncode != 0:
                    print(f"  WARN: clone failed for {r['name']}: {result.stderr.strip()}", file=sys.stderr)
                    continue
            sha_result = subprocess.run(
                ["git", "-C", str(dest), "rev-parse", "HEAD"],
                capture_output=True, text=True,
            )
            if sha_result.returncode != 0:
                print(f"  WARN: could not get HEAD SHA for {r['name']}", file=sys.stderr)
                continue
            real_sha = sha_result.stdout.strip()
            if r["commit"] != real_sha:
                r["commit"] = real_sha
                updated = True
            print(f"  {r['name']}: {real_sha}")
        if updated:
            with open(CORPUS_YAML, "w") as f:
                yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"corpus.yaml updated with real SHAs.")
        print(f"Corpus ready: {CORPUS_DIR}")
        return

    for r in repos:
        dest = CORPUS_DIR / r["name"]
        if dest.exists():
            print(f"  skip (exists): {r['name']}")
            continue
        print(f"  cloning {r['name']} ...")
        subprocess.run(["git", "clone", r["url"], str(dest)], check=True)
        subprocess.run(["git", "-C", str(dest), "checkout", r["commit"]], check=True)
        print(f"  done: {r['name']}")

    print(f"Corpus ready: {CORPUS_DIR}")


if __name__ == "__main__":
    main()
