import os
from typing import Dict, Any, Iterator
from src.thor2timesketch import constants
from src.thor2timesketch.exceptions import ProcessingError, MappingError, VersionError
from src.thor2timesketch.input.json_reader import JsonReader
from src.thor2timesketch.config.logger import LoggerConfig
from src.thor2timesketch.mappers.json_log_version import JsonLogVersion
from src.thor2timesketch.mappers.mapper_loader import load_all_mappers

logger = LoggerConfig.get_logger(__name__)


class JsonTransformer:
    def __init__(self) -> None:
        load_all_mappers()
        self.input_reader = JsonReader()
        self.log_version_mapper = JsonLogVersion()
        self.mb_converter = constants.MB_CONVERTER

    def transform_thor_logs(self, input_json_file: str) -> Iterator[Dict[str, Any]]:
        valid_thor_logs = self.input_reader.get_valid_data(input_json_file)
        if valid_thor_logs is None:
            message_err = "No valid THOR logs found"
            logger.error(message_err)
            raise ProcessingError(message_err)

        file_size = os.path.getsize(input_json_file)
        logger.info(f"Processing input file: {input_json_file} ({file_size / self.mb_converter:.2f} MB)")
        return self._generate_mapped_logs(valid_thor_logs)

    def _generate_mapped_logs(self, valid_thor_logs: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for json_line in valid_thor_logs:
            try:
                version_mapper = self.log_version_mapper.get_mapper_for_version(json_line)
                mapped_events = version_mapper.map_thor_events(json_line)

                for event in mapped_events:
                    yield event

            except VersionError as e:
                message_err = f"Error mapping THOR log version: {e}"
                logger.error(message_err)
                raise MappingError(message_err)

            except Exception as e:
                message_err = f"Error mapping THOR log: {e}"
                logger.error(message_err)
                raise MappingError(message_err)

    logger.debug("Finished transforming THOR logs")