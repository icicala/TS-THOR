import time
from pathlib import Path
from typing import Dict, Union, Any, Iterator
from rich.progress import Progress, TextColumn, SpinnerColumn
from timesketch_import_client import importer
from timesketch_api_client import config as timesketch_config
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.constants import TS_SCOPE
from thor2timesketch.exceptions import TimesketchError

class TSIngest:

    def __init__(self, thor_file: Path, sketch: str) -> None:
        self.thor_file = thor_file
        self.ts_client = timesketch_config.get_client()
        if not self.ts_client:
            raise TimesketchError(
                "Failed to connect to Timesketch client. Check your configuration."
            )
        self.timeline_name: str = self.thor_file.stem
        sketch_type: Union[int, str] = self._identify_sketch_type(sketch)
        self.my_sketch: Any = self._load_sketch(sketch_type)


    def _identify_sketch_type(self, sketch: str) -> Union[int, str]:
        return int(sketch) if sketch.isdigit() else sketch

    def _get_available_sketches(self) -> Dict[str, int]:
        sketches: dict[str, int] = {}
        try:
            for scope in TS_SCOPE:
                for sketch in self.ts_client.list_sketches(
                    scope=scope, include_archived=False
                ):
                    sketches[sketch.name] = int(sketch.id)
            return sketches
        except Exception as error:
            error_msg = f"fFailed to retrieve sketches from Timesketch: {error}"
            ConsoleConfig.error(error_msg)
            raise TimesketchError(error_msg)

    def _load_sketch(self, sketch: Union[int, str]) -> Any:
        try:
            available_sketches = self._get_available_sketches()

            if isinstance(sketch, int) and sketch in available_sketches.values():
                my_sketch = self.ts_client.get_sketch(sketch)
                ConsoleConfig.info(f"Found sketch with ID {sketch}: {my_sketch.name}")
                return my_sketch

            if isinstance(sketch, str) and sketch in available_sketches.keys():
                my_sketch = self.ts_client.get_sketch(available_sketches[sketch])
                ConsoleConfig.info(f"Found sketch with name '{sketch}': ID {my_sketch.id}")
                return my_sketch

            ConsoleConfig.info("Creating a new sketch with name `{sketch}`")
            new_sketch = self.ts_client.create_sketch(
                sketch, "Created by thor2ts"
            )
            if not new_sketch or not hasattr(new_sketch, "id"):
                raise TimesketchError("Failed to create sketch with name `{sketch}`")
            ConsoleConfig.info(
                f"New sketch has been created with name: '{new_sketch.name}' and ID: {new_sketch.id}"
            )
            return new_sketch
        except Exception as error:
            error_msg = f"Failed to load sketch: {error}"
            ConsoleConfig.error(error_msg)
            raise TimesketchError(error_msg)

    def ingest_events(self, events: Iterator[Dict[str, Any]]) -> None:

        try:
            self.ts_client.get_sketch(self.my_sketch.id)
        except Exception:
            error_msg = f"Sketch ID `{self.my_sketch.id}` not found, aborting ingest"
            ConsoleConfig.error(error_msg)
            TimesketchError(error_msg)

        processed_count = error_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            TextColumn("[cyan]{task.completed} processed"),
            TextColumn("• [red]{task.fields[errors]} errors"),
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"[bold green]Ingesting to sketch '{self.my_sketch.name}'",
                total=None,
                completed=0,
                errors=0,
                sketch_name=self.my_sketch.name,
            )
            try:
                with importer.ImportStreamer() as streamer:
                    streamer.set_sketch(self.my_sketch)
                    streamer.set_timeline_name(self.timeline_name)
                    streamer.set_provider("thor2ts")
                    streamer.set_upload_context(self.timeline_name)

                    for event in events:
                        try:
                            streamer.add_dict(event)
                            processed_count += 1
                        except Exception as e:
                            error_count += 1
                            ConsoleConfig.debug(f"Error adding event to streamer: '{e}'")
                        finally:
                            progress.update(
                                task, completed=processed_count, errors=error_count
                            )
                if not streamer.timeline:
                    raise TimesketchError(
                        "Error creating timeline, ingestion aborted"
                    )

                progress.update(task, description="[bold yellow]Indexing timeline…")
                deadline = time.time() + 60
                timeout_reached = False
                while (
                    streamer.state.lower() not in ("ready", "success")
                    and not timeout_reached
                ):
                    if time.time() > deadline:
                        ConsoleConfig.warning(
                            "Indexing did not complete within 60 seconds - the timeline will continue to be indexed in the background"
                        )
                        timeout_reached = True
                    time.sleep(1)
                if not timeout_reached:
                    progress.update(task, description="[bold green]Indexing complete")

            except KeyboardInterrupt:
                ConsoleConfig.warning("Timesketch ingestion interrupted by user")
                raise
            except Exception as error:
                error_msg = f"Failed to ingest events: {error}"
                ConsoleConfig.error(error_msg)
                raise TimesketchError(error_msg)

        ConsoleConfig.success(
            f"Processed {processed_count} events for sketch '{self.my_sketch.name}'"
        )
        if error_count > 0:
            ConsoleConfig.warning(f"Encountered {error_count} errors during ingestion")
