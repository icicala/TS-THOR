import os
from typing import Generator, Dict, Any, Iterator
from thor_ts_mapper import constants
from thor_ts_mapper.exceptions import ProcessingError, MappingError, JsonFlatteningError
from thor_ts_mapper.thor_input_reader import THORJSONInputReader
from thor_ts_mapper.thor_json_flattener import THORJSONFlattener
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.thor_json_log_version import THORJSONLogVersionMapper

logger = LoggerConfig.get_logger(__name__)


class THORJSONTransformer:
    def __init__(self):
        self.input_reader = THORJSONInputReader()
        self.flattener = THORJSONFlattener()
        self.log_version_mapper = THORJSONLogVersionMapper()
        self.mb_converter = constants.MB_CONVERTER

    def transform_thor_logs(self, input_json_file) -> Iterator[Dict[str, Any]]:
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
                flattened_json = self.flattener.flatten_jsonl(json_line)
                version_mapper = self.log_version_mapper.get_mapper(flattened_json)
                mapped_events = version_mapper.map_thor_events(flattened_json)

                for event in mapped_events:
                    yield event

            except JsonFlatteningError as e:
                message_err = f"Error flattening JSON log: {e}"
                logger.error(message_err)
                raise MappingError(message_err)

            except Exception as e:
                message_err = f"Error mapping THOR log: {e}"
                logger.error(message_err)
                raise MappingError(message_err)

        logger.debug("Finished transforming THOR logs")

input_file = "../thor10_7_old_json.json"
transformer = THORJSONTransformer()
mapped_logs = transformer.transform_thor_logs(input_file)
for log in mapped_logs:
    print(log)