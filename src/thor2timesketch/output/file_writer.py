import os
import json
from typing import Dict, Any, Iterator
from thor2timesketch.config.logger import LoggerConfig
from rich.progress import Progress, TextColumn, SpinnerColumn
from thor2timesketch import constants
from thor2timesketch.exceptions import OutputError

logger = LoggerConfig.get_logger(__name__)


class FileWriter:
    def __init__(self, output_file: str):
        self.output_file = output_file
        file_name, extension = os.path.splitext(self.output_file)
        if extension.lower() != constants.OUTPUT_FILE_EXTENSION:
            self.output_file = file_name + constants.OUTPUT_FILE_EXTENSION
            logger.info(f"Changed output file to `{self.output_file}` to ensure JSONL format")

    def _cleanup_temp_file(self, temp_file: str) -> None:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                logger.debug(f"Removed temporary file: {temp_file}")
            except OSError as e:
                logger.warning(f"Failed to remove temporary file: {e}")

    def write_to_file(self, events: Iterator[Dict[str, Any]]) -> None:
        temp_file = f"{self.output_file}.tmp"

        try:
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.isdir(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")

            processed_count = 0
            error_count = 0
            output_filename = os.path.basename(self.output_file)

            with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]Writing to '{task.fields[filename]}'"),
                    TextColumn("[cyan]{task.completed} processed"),
                    TextColumn("• [red]{task.fields[errors]} errors"),
                    transient=True
            ) as progress:
                task = progress.add_task(
                    "Writing", total=None, completed=0, errors=0,
                    filename=output_filename
                )

                with open(temp_file, 'w', encoding=constants.DEFAULT_ENCODING) as file:
                    for event in events:
                        try:
                            file.write(json.dumps(event) + "\n")
                            processed_count += 1
                        except Exception as e:
                            error_count += 1
                            logger.debug(f"Error writing event: {e}")
                        finally:
                            progress.update(task, completed=processed_count, errors=error_count)

            if error_count > 0:
                logger.warning(f"Encountered {error_count} errors while writing {processed_count} events")
                self._cleanup_temp_file(temp_file)
                raise OutputError(f"File processing failed with {error_count} errors")
            else:
                os.replace(temp_file, self.output_file)
                logger.info(f"Successfully written {processed_count} events to {self.output_file}")

        except KeyboardInterrupt:
            logger.warning("Process interrupted by user")
            self._cleanup_temp_file(temp_file)
            raise
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            self._cleanup_temp_file(temp_file)
            raise OutputError(str(e))