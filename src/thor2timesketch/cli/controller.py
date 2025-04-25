import logging
import os
import sys
from typing import Optional
import typer
from rich.console import Console
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.transformation.json_transformer import JsonTransformer
from thor2timesketch.output.file_writer import FileWriter
from thor2timesketch.output.ts_ingest import TSIngest
from thor2timesketch.exceptions import InputError, ProcessingError, OutputError, Thor2tsError

app = typer.Typer(help="thor2ts: Convert THOR security scanner logs to Timesketch format", add_completion=True)
console = Console()

def version_callback(value: bool):
    if value:
        from thor2timesketch import __version__
        typer.echo(f"thor2timesketch version: {__version__}")
        raise typer.Exit()

@app.command()
def main(
        input_file: str = typer.Argument(..., help="Path to THOR JSON log file"),
        output_file: Optional[str] = typer.Option(None, "--output-file", "-o",
                                                  help="Write output to specified JSONL file"),
        sketch: Optional[str] = typer.Option(None, "--sketch",
                                             help="Sketch ID or name for ingesting events into Timesketch"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose debugging output"),
        version: Optional[bool] = typer.Option(
            None, "--version", callback=version_callback, is_eager=True, help="Show version and exit"
        )
):

    log_level = logging.DEBUG if verbose else logging.INFO
    LoggerConfig.setup_root_logger(level=log_level)
    logger = LoggerConfig.get_logger(__name__)

    if not os.path.isfile(input_file):
        console.print(f"[bold red]Error:[/] Input file not found: {input_file}")
        raise typer.Exit(code=1)

    if sketch and sketch.isdigit():
        sketch = int(sketch)

    output_to_file = output_file is not None
    output_to_ts = sketch is not None

    if not (output_to_file or output_to_ts):
        console.print("[bold red]Error:[/] No output destination specified. Use -o/--output-file for file output or --sketch for Timesketch ingestion.")
        raise typer.Exit(code=1)

    try:
        mapped_events = JsonTransformer().transform_thor_logs(input_json_file=input_file)

        if output_to_file:
            write_to_file = FileWriter(output_file)
            write_to_file.write_to_file(mapped_events)

        if output_to_ts:
            upload_to_ts = TSIngest(thor_file=input_file, sketch=sketch)
            upload_to_ts.ingest_events(mapped_events)

        logger.info("THOR log processing completed successfully")

    except KeyboardInterrupt:
        logger.warning("Processing interrupted by user")
        raise typer.Exit(code=130)
    except InputError as e:
        logger.error(f"Input validation error: {e}", exc_info=verbose)
        raise typer.Exit(code=2)
    except ProcessingError as e:
        logger.error(f"Processing error: {e}", exc_info=verbose)
        raise typer.Exit(code=3)
    except OutputError as e:
        logger.error(f"Output error: {e}", exc_info=verbose)
        raise typer.Exit(code=4)
    except Thor2tsError as e:
        logger.error(f"Thor2ts error: {e}", exc_info=verbose)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=verbose)
        raise typer.Exit(code=1)