from typing import Dict, Any, List, Optional
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.mappers.mapper_json_v1 import MapperJsonV1
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.utils.normalizer import FlatteningNormalizer
from thor2timesketch.utils.regex_timestamp_extractor import RegexTimestampExtractor

@JsonLogVersion.log_version("v2.0.0")
class MapperJsonV2(MapperJsonBase):
    THOR_TIMESTAMP_FIELD: str = "time"
    THOR_MESSAGE_FIELD: str = "message"
    THOR_MODULE_FIELD: str = "module"
    THOR_LEVEL_FIELD: str = "level"

    def __init__(self) -> None:
        self.normalizer = FlatteningNormalizer()
        self.timestamp_extractor = RegexTimestampExtractor()
        self.mapper = MapperJsonV1()
        super().__init__(self.normalizer, self.timestamp_extractor)

    def map_thor_events(self, json_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        flattened_json = self.normalizer.normalize(json_log)
        return super().map_thor_events(flattened_json)

    def _get_message(self, json_log: Dict[str, Any]) -> str:
        return self.mapper._get_message(json_log)

    def _get_timestamp_desc(self, json_log: Dict[str, Any], time_data: DatetimeField) -> str:
        return self.mapper._get_timestamp_desc(json_log, time_data)

    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        return self.mapper._get_additional_fields(json_log)

    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> DatetimeField:
        return self.mapper._get_thor_timestamp(json_log)

    def get_filterable_fields(self, json_log: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        return self.mapper.get_filterable_fields(json_log)

    def _get_thor_tags(self, json_log: Dict[str, Any]) -> List[str]:
        return self.mapper._get_thor_tags(json_log)

    def _get_additional_tags(self, json_log: Dict[str, Any]) -> List[str]:
        return self.mapper._get_additional_tags(json_log)