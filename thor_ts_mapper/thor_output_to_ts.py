import json

from timesketch_import_client import importer
from timesketch_api_client import config as timesketch_config
from tqdm import tqdm

from thor_ts_mapper.logger_config import LoggerConfig
logger = LoggerConfig.get_logger(__name__)



class THORIngestToTS:
    """Handles communication with Timesketch"""

    def __init__(self):
        self.api = None
        self.config_assistant = None

    def connect(self):
        """Connect to Timesketch API"""
        try:
            self.api = timesketch_config.get_client(load_cli_config=True)
            if not self.api:
                raise ConnectionError("Failed to initialize Timesketch client")

            self.config_assistant = timesketch_config.ConfigAssistant()
            self.config_assistant.load_config_file(load_cli_config=True)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Timesketch: {e}")
            return False

    def get_sketch(self, sketch_id=None):
        """Get sketch by ID or from config"""
        if not self.api:
            return None

        try:
            if sketch_id:
                sketch = self.api.get_sketch(sketch_id=int(sketch_id))
            else:
                sketch_from_config = self.config_assistant.get_config("sketch")
                if not sketch_from_config:
                    logger.error("No sketch ID provided or found in config")
                    return None
                sketch = self.api.get_sketch(sketch_id=int(sketch_from_config))

            # Check if we have access
            sketch.name
            return sketch
        except Exception as e:
            logger.error(f"Error accessing sketch: {e}")
            return None

    def ingest_file(self, sketch, file_path, timeline_name):
        """Ingest a file into Timesketch"""
        try:
            with open(file_path, 'r') as f:
                data = f.read()

            with importer.ImportStreamer() as streamer:
                streamer.set_sketch(sketch)
                streamer.set_timeline_name(timeline_name)

                logger.info(f"Ingesting events into Timesketch timeline '{timeline_name}'")
                events_count = 0

                for line in tqdm(data.strip().split('\n'), desc="Ingesting events"):
                    event = json.loads(line)
                    streamer.add_dict(event)
                    events_count += 1

            logger.info(f"Successfully ingested {events_count} events into Timesketch")
            return True, events_count
        except Exception as e:
            logger.error(f"Error ingesting file into Timesketch: {e}")
            return False, 0