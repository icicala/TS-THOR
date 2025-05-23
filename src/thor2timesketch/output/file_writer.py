import os
import json
from typing import Dict, Any, Iterator, Union

from pycparser.ply.yacc import error_count

from thor2timesketch.config.console_config import ConsoleConfig
from rich.progress import Progress, TextColumn, SpinnerColumn
from thor2timesketch.constants import OUTPUT_FILE_EXTENSION, DEFAULT_ENCODING, MAX_WRITE_ERRORS
from thor2timesketch.exceptions import OutputError
from pathlib import Path

class FileWriter:
    def __init__(self, output_file: Path):
        self.output_file = output_file

    def _normalize_extension(self) -> None:
        if self.output_file.suffix.lower() != OUTPUT_FILE_EXTENSION:
            self.output_path = self.output_file.with_suffix(OUTPUT_FILE_EXTENSION)
            ConsoleConfig.info(f"Changed output file to '{self.output_path}' to ensure JSONL format")

    def _prepare_output_dir(self) -> None:
        output_dir = self.output_path.parent
        if output_dir and not output_dir.is_dir():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                ConsoleConfig.info(f"Created output directory: '{output_dir}'")
            except OSError as e:
                ConsoleConfig.error(f"Failed to create output directory {output_dir}`: {e}")
                raise OutputError(f"Cannot create output directory: {e}")

    def _cleanup_file(self) -> None:
        if self.output_path.exists():
            try:
                self.output_path.unlink()
                ConsoleConfig.debug(f"Removed output file: '{self.output_path}'")
            except OSError as e:
                ConsoleConfig.error(f"Failed to remove output file: {e}")
                raise OutputError(f"Cannot remove output file: {e}")

    def write_to_file(self, events: Iterator[Dict[str, Any]]) -> None:
        self._normalize_extension()
        self._prepare_output_dir()
        mode = "a" if self.output_path.exists() else "w"
        action = "Appending to" if mode == "a" else "Writing to"
        ConsoleConfig.info(f"'{action}' file: '{self.output_file}'")
        try:
            processed_count = error_count = 0
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold green]Writing to '{task.fields[filename]}'"),
                TextColumn("[green]{task.completed} processed"),
                TextColumn("• [red]{task.fields[errors]} errors"),
                transient=True,
            ) as progress:
                task = progress.add_task(
                    "Writing",
                    total=None,
                    completed=0,
                    errors=0,
                    filename=self.output_path.name,
                )

                with self.output_path.open(mode, encoding=DEFAULT_ENCODING) as file:
                    for event in events:
                        try:
                            file.write(json.dumps(event) + "\n")
                            processed_count += 1
                        except (TypeError, ValueError, OSError) as e:
                            error_count += 1
                            if error_count <= MAX_WRITE_ERRORS:
                                logger.error(f"Error writing event to file: {e}")
                        finally:
                            progress.update(
                                task, completed=processed_count, errors=error_count
                            )

            if error_count:
                ConsoleConfig.error(
                    f"Encountered '{error_count}' errors while writing '{processed_count}' events"
                )
                self._cleanup_file()
                raise OutputError(f"File processing failed with {error_count} errors")
            ConsoleConfig.success(f"Successfully wrote '{processed_count}' events to '{self.output_file}'")

        except KeyboardInterrupt:
            ConsoleConfig.warning("Process interrupted by user")
            self._cleanup_file()
            raise

        except Exception as e:
            ConsoleConfig.error(f"Error writing to file: {e}")
            self._cleanup_file()
            raise OutputError(str(e))
