import os
from typing import Dict, Any, Iterator, Optional
from thor2timesketch.config.filter_findings import FilterFindings
from thor2timesketch.constants import MB_CONVERTER
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.input.json_reader import JsonReader
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_loader import load_all_mappers
from thor2timesketch.transformation.pretransformation_processor import PreTransformationProcessor
from pathlib import Path

class JsonTransformer:

    def __init__(self) -> None:
        load_all_mappers()
        self.reader = JsonReader()
        self.version_mapper = JsonLogVersion()
        self.mb = MB_CONVERTER

    def transform_thor_logs(
        self, input_file: Path, filter_path: Optional[Path]
    ) -> Iterator[Dict[str, Any]]:

        selectors = FilterFindings.read_filters_yaml(filter_path)
        pre_transform = PreTransformationProcessor(filter_path)
        raw_lines = self.reader.get_valid_data(input_file)

        self._log_start(input_file)
        yield from self._generate_events(raw_lines, selectors, pre_transform)
        self._log_end(input_file)

    def _generate_events(
        self,
        events: Iterator[Dict[str, Any]],
        selectors: FilterFindings,
        pre_transform: PreTransformationProcessor,
    ) -> Iterator[Dict[str, Any]]:
        for entry in events:
            for record in pre_transform.transformation(entry):
                mapper = self.version_mapper.get_mapper_for_version(record)
                if self._is_eligible(record, mapper, selectors):
                    yield from mapper.map_thor_events(record)

    def _is_eligible(
        self, record: Dict[str, Any], mapper, selectors: FilterFindings
    ) -> bool:
        if not mapper.requires_filter():
            return True
        level, module = mapper.get_filterable_fields(record)
        return selectors.matches_filter_criteria(level, module)

    def _log_start(self, input_file: Path) -> None:
        size = os.path.getsize(input_file) / self.mb
        ConsoleConfig.info(f"Starting transforming events from input file: `{input_file}` ({size:.2f} MB)")

    def _log_end(self, input_file: Path) -> None:
        ConsoleConfig.success(f"Finished transforming events from input file: `{input_file}`")
