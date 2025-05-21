import os
from typing import Dict, Any, Iterator, Optional
from thor2timesketch.constants import MB_CONVERTER
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_loader import load_all_mappers
from thor2timesketch.transformation.filter_processor import FilterProcessor
from thor2timesketch.transformation.mapper_processor import MapperProcessor
from thor2timesketch.transformation.pretransformation_processor import PreTransformationProcessor
from thor2timesketch.transformation.reader_processor import ReaderProcessor

logger = LoggerConfig.get_logger(__name__)


class JsonTransformer:
    def __init__(self) -> None:
        load_all_mappers()
        self.input_reader = ReaderProcessor()
        self.pre_transformer = PreTransformationProcessor()
        self.log_version_mapper = JsonLogVersion()
        self.mb_converter = MB_CONVERTER

    def transform_thor_logs(self, input_json_file: str, filter_path: Optional[str]) -> Iterator[Dict[str, Any]]:

        raw_events = self.input_reader.read(input_json_file)
        file_size = os.path.getsize(input_json_file)
        logger.info(f"Processing input file: '{input_json_file}' ('{file_size / self.mb_converter:.2f}' MB)")
        for event in raw_events:
            pre_transformed_events = self.pre_transformer.pre_transformer(event)
            mappers_events = MapperProcessor(self.log_version_mapper).map(pre_transformed_events)
            filtered_events = FilterProcessor(self.log_version_mapper, filter_path).filter(mappers_events)
            for mapper, filtered_event in filtered_events:
                yield from mapper.map_thor_events(filtered_event)

        logger.debug(f"Finished processing input file: '{input_json_file}'")


json_v1 = "../../../thoraudittrail7mail.json"
transformer = JsonTransformer()
for eveng in transformer.transform_thor_logs(json_v1, None):
    print(eveng)