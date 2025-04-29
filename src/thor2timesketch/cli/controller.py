import logging
from pathlib import Path
from typing import Optional
import typer
from importlib.metadata import version, PackageNotFoundError
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.exceptions import Thor2tsError
from thor2timesketch.output.output_writer import OutputWriter
from thor2timesketch.transformation.json_transformer import JsonTransformer

app = typer.Typer(
    no_args_is_help=True,
    add_completion=True,
)
logger = LoggerConfig.get_logger(__name__)

def _version_callback(value: bool) -> None:
    if not value:
        return
    try:
        pkg_version = version("thor2timesketch")
    except PackageNotFoundError:
        pkg_version = "0.0.0"
    typer.echo(f"thor2timesketch version: {pkg_version}")
    raise typer.Exit()

@app.callback(invoke_without_command=True)
def _setup(
    _version_flag: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit",
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose", help="Enable debug-level logging"
    ),
) -> None:

    level = logging.DEBUG if verbose else logging.INFO
    LoggerConfig.setup_root_logger(level=level)

@app.command()
def main(
    input_file: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False, help="THOR JSON log file"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "-o", "--output-file", help="Write output JSONL"
    ),
    sketch: Optional[str] = typer.Option(
        None, "--sketch", help="Sketch ID or name for Timesketch ingest"
    ),
) -> None:

    if not (output_file or sketch):
        typer.secho(
            "Error: you must specify --output-file or --sketch",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    try:
        logger.debug(f"Transforming {input_file}")
        events = JsonTransformer().transform_thor_logs(input_json_file=str(input_file))

        logger.debug("Writing output")
        OutputWriter(str(input_file), output_file, sketch).write(events)

        logger.info("✅ thor2ts completed successfully.")
    except KeyboardInterrupt:
        logger.warning("⚠️ Processing interrupted by user")
        raise typer.Exit(130)
    except Thor2tsError as e:
        logger.error(f"🚨 thor2ts error: {e}", exc_info=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}", exc_info=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
