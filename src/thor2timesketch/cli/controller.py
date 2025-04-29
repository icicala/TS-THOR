import logging
from pathlib import Path
from typing import Optional

import typer
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.exceptions import Thor2tsError
from thor2timesketch.output.output_writer import OutputWriter
from thor2timesketch.transformation.json_transformer import JsonTransformer

app = typer.Typer(
    help="thor2ts: Convert THOR security scanner logs to Timesketch format",
    add_completion=True,
)

def _version_callback(value: bool) -> None:
    if value:
        from thor2timesketch import __version__
        typer.echo(f"thor2timesketch version: {__version__}")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def setup_environment(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
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
    ctx.obj = {"logger": LoggerConfig.get_logger(__name__)}


@app.command()
def main(
    ctx: typer.Context,
    input_file: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False, help="Path to THOR JSON log file"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "-o", "--output-file", help="Write output to specified JSONL file"
    ),
    sketch: Optional[str] = typer.Option(
        None, "--sketch", help="Sketch ID or name for ingesting events into Timesketch"
    ),
) -> None:
    logger: logging.Logger = ctx.obj["logger"]

    if not (output_file or sketch):
        typer.secho(
            "Error: you must specify --output-file or --sketch",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        logger.debug(f"Transforming {input_file}")
        events = JsonTransformer().transform_thor_logs(input_json_file=str(input_file))

        logger.debug("Writing output")
        OutputWriter(str(input_file), output_file, sketch).write(events)

        logger.info("✅  thor2ts completed successfully.")
    except KeyboardInterrupt:
        logger.warning("⚠️  Processing interrupted by user")
        raise typer.Exit(code=130)
    except Thor2tsError as e:
        logger.error(f"🚨  thor2ts error: {e}", exc_info=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"💥  Unexpected error: {e}", exc_info=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
