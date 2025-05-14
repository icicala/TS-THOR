from typing import List, Dict, Any, Optional
from thor2timesketch.exceptions import MappingError, TimestampError
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch import constants

@JsonLogVersion.log_version("v1.0.0")
class MapperJsonV1(MapperJsonBase):

    THOR_TIMESTAMP_FIELD:str = "time"
    THOR_MESSAGE_FIELD: str = "message"
    THOR_MODULE_FIELD: str = "module"
    THOR_LEVEL_FIELD: str = "level"

    def _get_message(self, json_log: Dict[str, Any]) -> str:
        message = json_log.get(MapperJsonV1.THOR_MESSAGE_FIELD)
        if message is None:
            raise MappingError("Missing required 'message' field in JSON log")
        if not isinstance(message, str):
            raise MappingError(f"Invalid type for 'message': expected str, got {type(message).__name__}")
        return message

    def _get_timestamp_desc(self, json_log: Dict[str, Any], ts_data: Optional[DatetimeField] = None) -> str:
        if ts_data is None or ts_data.path == MapperJsonV1.THOR_TIMESTAMP_FIELD:
            return "THOR scan timestamp"
        module = json_log.get(MapperJsonV1.THOR_MODULE_FIELD)
        if module is None:
            raise MappingError("Missing required 'module' field for timestamp description")
        return f"{module} - {ts_data.path}"

    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        exclude_thor_timestamp = MapperJsonV1.THOR_TIMESTAMP_FIELD
        additional_fields = {
            key: value for key, value in json_log.items() if key not in (exclude_thor_timestamp)
        }
        return additional_fields

    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> DatetimeField:
        thor_timestamp = json_log.get(MapperJsonV1.THOR_TIMESTAMP_FIELD)
        if thor_timestamp is None:
            raise TimestampError(f"Missing required '{MapperJsonV1.THOR_TIMESTAMP_FIELD}' field in JSON log")
        if not isinstance(thor_timestamp, str):
            raise TimestampError(f"Invalid type for '{MapperJsonV1.THOR_TIMESTAMP_FIELD}': expected str, got {type(thor_timestamp).__name__}")
        return DatetimeField(path=MapperJsonV1.THOR_TIMESTAMP_FIELD, datetime=thor_timestamp)

    def _get_thor_tags(self, json_log: Dict[str, Any]) -> List[str]:
        type_event = json_log.get(MapperJsonV1.THOR_LEVEL_FIELD)
        if type_event is None:
            raise MappingError("Missing required 'level' field for tags")
        return [constants.THOR_TAG, type_event]

    def _get_additional_tags(self, json_log: Dict[str, Any]) -> List[str]:
        type_event = json_log.get(MapperJsonV1.THOR_LEVEL_FIELD)
        if type_event is None:
            raise MappingError("Missing required 'level' field for additional tags")
        return [constants.EXTRA_TAG, type_event]

    def get_filterable_fields(self, json_log: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        level = json_log.get(MapperJsonV1.THOR_LEVEL_FIELD)
        module = json_log.get(MapperJsonV1.THOR_MODULE_FIELD)
        return level, module