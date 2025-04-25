import os.path
from typing import Dict, Union, Any, Iterable
from rich.progress import Progress, BarColumn, TextColumn
from timesketch_import_client import importer
from timesketch_api_client import config as timesketch_config
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch import constants


logger = LoggerConfig.get_logger(__name__)

class TSIngest:


    def __init__(self, thor_file: str, sketch: Union[int, str]) -> None:
        self.ts_client = timesketch_config.get_client()
        self.timeline_name: str = self._get_timeline_name(thor_file)
        self.my_sketch: Any = self._load_sketch(sketch)

    def _get_timeline_name(self, thor_file: str) -> str:
        file_basename: str = os.path.basename(thor_file)
        file_name, _ = os.path.splitext(file_basename)
        return file_name

    def _get_available_sketches(self) -> Dict[str, int]:
        sketches = {}
        for scope in constants.TS_SCOPE:
            for sketch in self.ts_client.list_sketches(scope=scope, include_archived=False):
                sketches[sketch.name] = int(sketch.id)
        return sketches


    def _load_sketch(self, sketch: Union[int, str]) -> Any:
        sketches = self._get_available_sketches()

        if isinstance(sketch, int):
            if sketch in sketches.values():
                my_sketch = self.ts_client.get_sketch(sketch)
                logger.info(f"Found sketch with ID {sketch}: {my_sketch.name}")
                return my_sketch
            else:
                sketch = f"Sketch_{sketch}"

        elif isinstance(sketch, str):
            if sketch in sketches.keys():
                my_sketch = self.ts_client.get_sketch(sketches[sketch])
                logger.info(f"Found sketch with name '{sketch}': ID {my_sketch.id}")
                return my_sketch

        logger.info("Creating a new sketch with name '{}'".format(sketch))
        my_sketch = self.ts_client.create_sketch(sketch, "New sketch created by thor2ts")
        logger.info(f"New sketch has been created with name: '{my_sketch.name}' and ID: {my_sketch.id}")
        return my_sketch


    def ingest_events(self, events: Iterable[Dict[str, Any]]) -> None:
        with Progress(
                SpinnerColumn("dots"),  # Try dots, arrow3, line, dots12
                TextColumn("[bold blue]{task.description}")
        ) as progress:
            task = progress.add_task(f"Writing to {os.path.basename(self.output_file)}", total=None)
            with importer.ImportStreamer() as streamer:
                streamer.set_sketch(self.my_sketch)
                streamer.set_timeline_name(self.timeline_name)
                streamer.set_upload_context(self.timeline_name)
                for event in events:
                    try:
                        ok = streamer.add_dict(event)
                        if not ok:
                            logger.error("SKIPPED event: %s", {
                                key: event.get(key) for key in ("message", "datetime", "timestamp_desc")
                            })
                        progress.update(task, advance=1)
                    except Exception as e:
                        logger.error(f"Error adding event to streamer: '{e}'")
            logger.info(f"Successfully ingested events into sketch '{self.my_sketch.name}'")
            logger.info("The timeline will continue to be indexed in the background")