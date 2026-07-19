"""Verify pinned dependency versions are installed.

If this test fails, it means either the environment is missing a pinned package
or a package was upgraded without updating the pin in pyproject.toml + docs/targets.md.
"""
import importlib.metadata
import pytest


MAF_CORE_PIN = "1.11.0"
AUTOGEN_AGENTCHAT_PIN = "0.4.9.3"
PYAUTOGEN_PIN = "0.2.35"


def _installed_version(pkg: str) -> str:
    return importlib.metadata.version(pkg)


def test_maf_core_version():
    assert _installed_version("agent-framework-core") == MAF_CORE_PIN


def test_autogen_agentchat_version():
    assert _installed_version("autogen-agentchat") == AUTOGEN_AGENTCHAT_PIN


def test_pyautogen_version():
    assert _installed_version("pyautogen") == PYAUTOGEN_PIN
