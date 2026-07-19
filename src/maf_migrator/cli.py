import typer
from maf_migrator import __version__

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
