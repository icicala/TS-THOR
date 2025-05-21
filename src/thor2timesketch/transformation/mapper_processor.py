from typing import Dict, Any, Iterator, Tuple
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase


class MapperProcessor:
    def __init__(self, log_version: JsonLogVersion) -> None:
        self.log_version = log_version

    def map(self, json_line: Iterator[Dict[str, Any]]) -> Iterator[Tuple[MapperJsonBase, Dict[str, Any]]]:
        for line in json_line:
            mapper = self.log_version.get_mapper_for_version(line)
            yield mapper, line



