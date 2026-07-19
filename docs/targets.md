# Package Targets

Verified against PyPI and the official Microsoft Agent Framework repository on 2026-07-19.
Do not update these pins from memory — re-verify against PyPI before changing.

## Migration target: Microsoft Agent Framework (MAF)

| Package | PyPI version | Import name | PyPI link |
|---------|-------------|-------------|-----------|
| `agent-framework-core` | **1.11.0** | `agent_framework` | https://pypi.org/project/agent-framework-core/ |

`agent-framework-core` is the minimal core package. The `agent-framework` meta-package
(https://pypi.org/project/agent-framework/) bundles all integration sub-packages; it
installs `agent-framework-core` plus extras for OpenAI, Azure, Foundry, etc.

Official repo: https://github.com/microsoft/agent-framework
Official docs: https://learn.microsoft.com/en-us/agent-framework/

`agent_framework.__version__` reports `"0.0.0"` because the module resolves its version from
`importlib.metadata.version("agent_framework")` (the import name) rather than the
distribution name `"agent-framework-core"`. Always use
`importlib.metadata.version("agent-framework-core")` to check the installed version.

## Migration sources: AutoGen

### v0.4 line (primary focus)

| Package | PyPI version | Import name | PyPI link |
|---------|-------------|-------------|-----------|
| `autogen-agentchat` | **0.4.9.3** | `autogen_agentchat` | https://pypi.org/project/autogen-agentchat/ |

This is the last patch release in the 0.4.x series (before the 0.5 restructure).
It is the primary migration source — the majority of actively maintained repos use
the `autogen_agentchat` import surface.

### Legacy v0.2 line

| Package | PyPI version | Import name | PyPI link |
|---------|-------------|-------------|-----------|
| `pyautogen` | **0.2.35** | `autogen` | https://pypi.org/project/pyautogen/ |

Legacy codebases use `import autogen` (note: bare `autogen` import name, not
`pyautogen`). This is the original Microsoft AutoGen before the v0.4 rewrite.
The `$999` tier targets this population.

## Notes

- These packages are dev-only extras (`pip install -e ".[dev]"`). They are never
  runtime dependencies of the migrator itself — the migrator only reads source code
  (via LibCST), it does not import the user's codebase.
- Pin drift is caught by `tests/test_package_pins.py`.
- AutoGen versions beyond 0.5.x (0.6, 0.7 …) share the same `autogen_agentchat`
  import surface as 0.4 but have API differences. The corpus inventory (item 1.2)
  will quantify how many corpus repos actually use 0.4-era APIs vs later ones.
