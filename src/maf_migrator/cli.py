import json
from pathlib import Path
from typing import Optional

import typer

from maf_migrator import __version__
from maf_migrator.aggregator import aggregate, to_markdown
from maf_migrator.reporter import generate_report
from maf_migrator.scanner import scan, scan_to_json

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
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write report to this file instead of stdout."
    ),
    emit_json: bool = typer.Option(
        False, "--json", help="Emit raw JSON inventory instead of a human-readable report."
    ),
) -> None:
    """Scan a repo for AutoGen API usage and render a migration report.

    By default renders a human-readable migration report to stdout.
    Use --json for the raw JSON inventory (pipe-friendly).
    Use --output report.md to write the report to a file.
    """
    if not path.exists():
        typer.echo(f"Error: path does not exist: {path}", err=True)
        raise typer.Exit(1)

    if emit_json:
        typer.echo(scan_to_json(path))
        return

    result = scan(path)
    report = generate_report(result, path)

    if output:
        output.write_text(report, encoding="utf-8")
        typer.echo(f"Wrote {output}", err=True)
    else:
        typer.echo(report, nl=False)


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
