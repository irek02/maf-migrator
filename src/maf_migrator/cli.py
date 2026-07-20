from pathlib import Path

import typer

from maf_migrator import __version__
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
