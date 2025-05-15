import os
from typing import Dict, Any, Iterator, Optional
from thor2timesketch import constants
from thor2timesketch.exceptions import ProcessingError, MappingError, VersionError, InputError
from thor2timesketch.input.json_reader import JsonReader
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_loader import load_all_mappers
from thor2timesketch.config.filter_findings import FilterFindings

logger = LoggerConfig.get_logger(__name__)


class JsonTransformer:
    def __init__(self) -> None:
        load_all_mappers()
        self.input_reader = JsonReader()
        self.log_version_mapper = JsonLogVersion()
        self.mb_converter = constants.MB_CONVERTER

    def transform_thor_logs(self, input_json_file: str, filter_path: Optional[str]) -> Iterator[Dict[str, Any]]:
        try:
            valid_thor_logs = self.input_reader.get_valid_data(input_json_file)
            filters = FilterFindings.read_from_yaml(filter_path)
            file_size = os.path.getsize(input_json_file)
            logger.info(f"Processing input file: '{input_json_file}' ('{file_size / self.mb_converter:.2f}' MB)")
            return self._generate_mapped_logs(valid_thor_logs, filters)
        except InputError:
            raise
        except Exception as error:
            message_err = f"Error transforming THOR logs: {error}"
            logger.error(message_err)
            raise ProcessingError(message_err) from error

    def _generate_mapped_logs(self, valid_thor_logs: Iterator[Dict[str, Any]], filters: FilterFindings) -> Iterator[Dict[str, Any]]:

        for json_line in valid_thor_logs:
            try:
                version_mapper = self.log_version_mapper.get_mapper_for_version(json_line)
                level, module = version_mapper.get_filterable_fields(json_line)
                if filters.matches_filter_criteria(level, module):
                    mapped_events = version_mapper.map_thor_events(json_line)
                    for event in mapped_events:
                        yield event
            except VersionError as error:
                message_err = f"Error mapping THOR log version: {error}"
                logger.error(message_err)
                raise MappingError(message_err) from error

            except Exception as error:
                message_err = f"Error mapping THOR log: {error}"
                logger.error(message_err)
                raise MappingError(message_err) from error

        logger.debug("Finished transforming THOR logs")
jsonv1_data = "../../../thor13mayjsonv2.json"
transformer = JsonTransformer()
for event in transformer.transform_thor_logs(jsonv1_data, None):
    print(event)
