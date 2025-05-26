from typing import Optional
from importlib.metadata import version, PackageNotFoundError
import typer
from pathlib import Path
from thor2timesketch.config.filter_creator import FilterCreator
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.output.output_writer import OutputWriter
from thor2timesketch.transformation.json_transformer import JsonTransformer
from thor2timesketch.exceptions import Thor2tsError

app = typer.Typer(
    help="Convert THOR security scanner logs to Timesketch format",
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool) -> None:
    if value:
        try:
            pkg_version = version("thor2timesketch")
        except PackageNotFoundError:
            pkg_version = "0.0.0"
        ConsoleConfig.info(f"thor2timesketch version: `{pkg_version}`")
        raise typer.Exit()


@app.command()
def main(
    input_file: Path = typer.Argument(
        ..., help="Path to THOR JSON log file", metavar="INPUT_FILE"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write output to specified JSONL file"
    ),
    sketch: Optional[str] = typer.Option(
        None, "--sketch", help="Sketch ID or name for ingesting events into Timesketch"
    ),
    filter_path: Optional[Path] = typer.Option(
        None, "--filter", "-f", help="Path to YAML filter configuration"
    ),
    generate_filter: bool = typer.Option(
        False, "--generate-filter", help="Generate a filter YAML and exit"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose debugging output"
    ),
    _version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:

    ConsoleConfig.panel(
        "Convert THOR security scanner logs to Timesketch format",
        title="thor2ts powered by Nextron Systems",
        style="bold cyan",
    )

    ConsoleConfig.set_verbose(verbose)

    if not input_file.is_file():
        ConsoleConfig.error(f"Input file not found: '{input_file}'. Use -h for help.")
        raise typer.Exit(code=1)

    if generate_filter:
        try:
            FilterCreator(input_file).generate_yaml_file()
            raise typer.Exit()
        except Thor2tsError as e:
            ConsoleConfig.error(f"{e}")
            raise typer.Exit(code=1)

    if not (output_file or sketch):
        ConsoleConfig.error(
            "Use -o/--output for file output or --sketch for Timesketch ingestion. Use -h for help."
        )
        raise typer.Exit(code=1)

    try:
        mapped_events = JsonTransformer().transform_thor_logs(
            input_file=input_file, filter_path=filter_path
        )

        writer = OutputWriter(input_file, output_file, sketch)
        writer.write(mapped_events)

        ConsoleConfig.success("✓ thor2ts successfully completed")

    except KeyboardInterrupt:
        ConsoleConfig.warning("⚠ Processing interrupted by user")
        raise typer.Exit(code=130)
    except Thor2tsError as e:
        ConsoleConfig.error(f"{e}")
        raise typer.Exit(code=1)
    except Exception as e:
        ConsoleConfig.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)
