from thor2timesketch.config.filter_findings import FilterFindings
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from typing import Dict, Any, Iterator, Tuple, Optional

from thor2timesketch.mappers.mapper_json_base import MapperJsonBase


class FilterProcessor:
    def __init__(self, version_mapper: JsonLogVersion, filter_path: Optional[str] = None) -> None:
        self.resolver = version_mapper
        self.selectors = FilterFindings.read_filters_yaml(filter_path)

    def filter(self, events: Iterator[Tuple[MapperJsonBase, Dict[str, Any]]]) -> Iterator[Tuple[MapperJsonBase, Dict[str, Any]]]:
        for mapper, event in events:
            level, module = mapper.get_filterable_fields(event)
            if self.selectors.matches_filter_criteria(level, module):
                yield mapper, event