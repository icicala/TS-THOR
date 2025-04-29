import os
from typing import Optional
from importlib.metadata import version, PackageNotFoundError
import typer
from rich.console import Console
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.output.output_writer import OutputWriter
from thor2timesketch.transformation.json_transformer import JsonTransformer
from thor2timesketch.exceptions import Thor2tsError

app = typer.Typer(
    help="Convert THOR security scanner logs to Timesketch format",
    no_args_is_help=True,
    add_completion=True,
)

console = Console()
error_console = Console(stderr=True)


def version_callback(value: bool) -> None:
    try:
        pkg_version = version("thor2timesketch")
    except PackageNotFoundError:
        pkg_version = "0.0.0"
    console.print(f"[bold green]thor2timesketch[/] version: [cyan]{pkg_version}[/]")
    raise typer.Exit()

@app.command()
def main(
        input_file: str = typer.Argument(..., help="Path to THOR JSON log file"),
        output_file: Optional[str] = typer.Option(None, "--output-file", "-o",
                                                  help="Write output to specified JSONL file"),
        sketch: Optional[str] = typer.Option(None, "--sketch",
                                             help="Sketch ID or name for ingesting events into Timesketch"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose debugging output"),
        version: bool = typer.Option(False, "--version", callback=version_callback, is_eager=True,
                                     help="Show version and exit")
) -> None:

    log_level = "DEBUG" if verbose else "INFO"
    LoggerConfig.setup_root_logger(level=log_level)

    if not os.path.isfile(input_file):
        error_console.print(f"[bold red]Error:[/] Input file not found: '{input_file}'")
        raise typer.Exit(code=1)

    if not (output_file or sketch):
        error_console.print(
            "[bold red]Error:[/] No output destination specified. Use -o/--output-file for file output or --sketch for Timesketch ingestion.")
        raise typer.Exit(code=1)

    try:
        console.print("[blue]Transforming THOR logs...[/]")
        mapped_events = JsonTransformer().transform_thor_logs(input_json_file=input_file)

        writer = OutputWriter(input_file, output_file, sketch)
        writer.write(mapped_events)

        console.print("[green]✓ thor2ts successfully completed[/]")

    except KeyboardInterrupt:
        error_console.print("[yellow]⚠ Processing interrupted by user[/]")
        raise typer.Exit(code=130)
    except Thor2tsError as e:
        error_console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        error_console.print(f"[bold red]Unexpected error:[/] {e}")
        raise typer.Exit(code=1)