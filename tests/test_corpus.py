"""Integrated tests for corpus.yaml manifest and scripts/corpus.py --dry-run."""
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
CORPUS_YAML = REPO_ROOT / "corpus.yaml"
CORPUS_SCRIPT = REPO_ROOT / "scripts" / "corpus.py"

REQUIRED_FIELDS = {"name", "url", "commit", "license", "generation"}
VALID_GENERATIONS = {"v0.4", "v0.2", "mixed"}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _load_manifest():
    with open(CORPUS_YAML) as f:
        return yaml.safe_load(f)


def test_corpus_yaml_exists():
    assert CORPUS_YAML.exists(), "corpus.yaml must exist at repo root"


def test_corpus_yaml_loads():
    manifest = _load_manifest()
    assert isinstance(manifest, dict), "corpus.yaml must parse to a dict"
    assert "repos" in manifest, "corpus.yaml must have a 'repos' key"
    assert isinstance(manifest["repos"], list), "'repos' must be a list"


def test_corpus_yaml_has_enough_repos():
    manifest = _load_manifest()
    repos = manifest["repos"]
    assert len(repos) >= 20, f"Expected ≥20 repos, got {len(repos)}"


def test_corpus_yaml_schema():
    manifest = _load_manifest()
    for i, repo in enumerate(manifest["repos"]):
        missing = REQUIRED_FIELDS - set(repo.keys())
        assert not missing, f"repo[{i}] ({repo.get('name', '?')}) missing fields: {missing}"


def test_corpus_yaml_generation_values():
    manifest = _load_manifest()
    for i, repo in enumerate(manifest["repos"]):
        gen = repo.get("generation")
        assert gen in VALID_GENERATIONS, (
            f"repo[{i}] ({repo.get('name', '?')}) invalid generation: {gen!r}; "
            f"must be one of {VALID_GENERATIONS}"
        )


def test_corpus_yaml_commit_format():
    manifest = _load_manifest()
    for i, repo in enumerate(manifest["repos"]):
        commit = repo.get("commit", "")
        assert COMMIT_RE.match(commit), (
            f"repo[{i}] ({repo.get('name', '?')}) invalid commit: {commit!r}; "
            "must be a 40-char lowercase hex SHA"
        )


def test_corpus_yaml_url_format():
    manifest = _load_manifest()
    for i, repo in enumerate(manifest["repos"]):
        url = repo.get("url", "")
        assert url.startswith("https://github.com/"), (
            f"repo[{i}] ({repo.get('name', '?')}) url must start with https://github.com/: {url!r}"
        )


def test_corpus_dry_run():
    result = subprocess.run(
        [sys.executable, str(CORPUS_SCRIPT), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"corpus.py --dry-run exited {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "Dry run OK" in result.stdout, (
        f"Expected 'Dry run OK' in output; got: {result.stdout!r}"
    )
