import subprocess
import sys


def test_version_exits_zero():
    """maf-migrate --version should exit 0 and print a version string."""
    result = subprocess.run(
        ["maf-migrate", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"
    assert result.stdout.strip(), "expected version output on stdout"
