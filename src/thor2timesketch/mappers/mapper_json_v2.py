from typing import Dict, Any, Optional
from thor2timesketch.exceptions import MappingError
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.utils.datetime_field import DatetimeField


@JsonLogVersion.log_version("v1.0.0")
class MapperJsonV2(MapperJsonBase):

    THOR_TIMESTAMP_FIELD:str = "time"
    THOR_MESSAGE_FIELD: str = "message"
    THOR_MODULE_FIELD: str = "module"

    def _get_message(self, json_log: Dict[str, Any]) -> str:
        message = json_log.get(MapperJsonV2.THOR_MESSAGE_FIELD)
        if message is None:
            message = "THOR APT scanner message"
        return message

    def _get_timestamp_desc(self, json_log: Dict[str, Any], ts_data: Optional[DatetimeField] = None) -> str:
        if ts_data is None or ts_data.path == MapperJsonV2.THOR_TIMESTAMP_FIELD:
            return "THOR scan timestamp"
        module = json_log.get(MapperJsonV2.THOR_MODULE_FIELD)
        return f"{module} - {ts_data.path}"

    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        exclude_thor_timestamp = MapperJsonV2.THOR_TIMESTAMP_FIELD
        exclude_thor_message = MapperJsonV2.THOR_MESSAGE_FIELD
        exclude_thor_module = MapperJsonV2.THOR_MODULE_FIELD
        additional_fields = {
            key: value for key, value in json_log.items()
            if key not in (exclude_thor_timestamp, exclude_thor_message, exclude_thor_module)
        }
        return additional_fields

    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> Optional[Any]:
        thor_timestamp = json_log.get(MapperJsonV2.THOR_TIMESTAMP_FIELD)
        if thor_timestamp is None:
            raise MappingError("Missing THOR timestamp field in JSON log")
        return DatetimeField(MapperJsonV2.THOR_TIMESTAMP_FIELD, thor_timestamp)

    def check_thor_log(self, json_log: Dict[str, Any]) -> bool:
        return any(key.startswith("reason") for key in json_log.keys())