import json
from pathlib import Path
from typing import Optional

import typer

from maf_migrator import __version__
from maf_migrator.aggregator import aggregate, to_markdown
from maf_migrator.scanner import scan_to_json

app = typer.Typer(help="Migrate AutoGen Python codebases to Microsoft Agent Framework.")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"maf-migrate {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    pass


@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to the repo or directory to scan."),
) -> None:
    """Scan a repo for AutoGen API usage and emit a JSON inventory."""
    if not path.exists():
        typer.echo(f"Error: path does not exist: {path}", err=True)
        raise typer.Exit(1)
    typer.echo(scan_to_json(path))


@app.command()
def inventory(
    paths: list[Path] = typer.Argument(..., help="Paths to repos/directories to aggregate."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write Markdown table to this file instead of JSON to stdout."
    ),
) -> None:
    """Aggregate AutoGen construct frequencies across multiple repos.

    Emits a JSON frequency table to stdout, or writes a Markdown table
    to --output for use as docs/corpus-inventory.md.
    """
    for p in paths:
        if not p.exists():
            typer.echo(f"Error: path does not exist: {p}", err=True)
            raise typer.Exit(1)

    result = aggregate(paths)

    if output:
        output.write_text(to_markdown(result))
        typer.echo(f"Wrote {output}", err=True)
    else:
        typer.echo(json.dumps(result, indent=2))
