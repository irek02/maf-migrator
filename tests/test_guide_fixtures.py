"""Validity tests for guide fixture pairs (0.3).

These fixture pairs are pre-written acceptance tests for Phase 2 transforms.
They are ground truth from Microsoft's AutoGen→MAF migration guide.
This test does NOT run transforms — it only verifies the fixtures are well-formed.
"""
import ast
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "guide"


def _all_cases():
    if not FIXTURES_DIR.is_dir():
        return []
    return sorted(d for d in FIXTURES_DIR.iterdir() if d.is_dir())


def test_fixtures_dir_exists():
    assert FIXTURES_DIR.is_dir(), f"Fixture dir missing: {FIXTURES_DIR}"


def test_minimum_case_count():
    cases = _all_cases()
    assert len(cases) >= 5, f"Expected ≥5 guide fixture cases, found {len(cases)}: {[d.name for d in cases]}"


def test_every_case_has_both_files():
    cases = _all_cases()
    for case in cases:
        assert (case / "before.py").is_file(), f"Missing before.py in {case.name}"
        assert (case / "expected_after.py").is_file(), f"Missing expected_after.py in {case.name}"


def test_every_before_parses():
    for before in sorted(FIXTURES_DIR.glob("*/before.py")):
        source = before.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {before.parent.name}/before.py: {e}") from e


def test_every_after_parses():
    for after in sorted(FIXTURES_DIR.glob("*/expected_after.py")):
        source = after.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {after.parent.name}/expected_after.py: {e}") from e


def test_sources_md_exists():
    assert (FIXTURES_DIR / "SOURCES.md").is_file(), "Missing tests/fixtures/guide/SOURCES.md"
