from typing import Dict, Any, List, Optional
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.exceptions import TimestampError, MappingError
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.utils.timestamp_extractor import TimestampExtractor

logger = LoggerConfig.get_logger(__name__)


class MapperJsonBase:
    THOR_TIMESTAMP_FIELD: List[str] = []
    THOR_MESSAGE_FIELD: List[str] = []
    THOR_MODULE_FIELD: List[str] = []

    def __init__(self) -> None:
        self.timestamp_extractor: TimestampExtractor = TimestampExtractor()

    def map_thor_events(self, json_log: Dict[str, Any]) -> List[Dict[str, Any]]:

        all_timestamps: List[DatetimeField] = self._get_timestamp_extract(json_log)

        thor_timestamp: str = self._get_thor_timestamp(json_log)

        additional_timestamp: List[DatetimeField] = [ts_field for ts_field in all_timestamps if ts_field.datetime != thor_timestamp and ts_field.path != self.THOR_TIMESTAMP_FIELD]

        events: List[Dict[str, Any]] = []

        thor_event_map = self._create_thor_scan_event(json_log, thor_timestamp)

        events.append(thor_event_map)
        if additional_timestamp:
            for datetime in additional_timestamp:
                event = self._create_additional_timestamp_event(json_log, datetime, thor_timestamp)
                events.append(event)

        logger.debug(f"Mapped {len(events)} events")
        return events

    def _create_thor_scan_event(self, json_log: Dict[str, Any], thor_timestamp: str) -> Dict[str, Any]:
        event = {
            'message': self._get_message(json_log),
            'datetime': thor_timestamp,
            'timestamp_desc': self._get_timestamp_desc(json_log),
        }
        event.update(self._get_additional_fields(json_log))
        return event

    def _create_additional_timestamp_event(self, json_log: Dict[str, Any],
                                           ts_data: DatetimeField, thor_datetime: str) -> Dict[str, Any]:
        event = {
            'message': self._get_message(json_log),
            'datetime': ts_data.datetime,
            'timestamp_desc': self._get_timestamp_desc(json_log, ts_data),
            'time_thor_scan': thor_datetime
        }
        event.update(self._get_additional_fields(json_log))
        return event

    def _get_timestamp_extract(self, json_log: Dict[str, Any]) -> List[DatetimeField]:
        return self.timestamp_extractor.extract_datetime(json_log)

    def _get_message(self, json_log: Dict[str, Any]) -> str:
        message = self._get_value_from_json(json_log, self.THOR_MESSAGE_FIELD)
        if not message:
            logger.debug("No message found in THOR event, using default message.")
            message = "THOR APT scanner message."
        return str(message)

    def _get_timestamp_desc(self, json_log: Dict[str, Any], ts_data: Optional[DatetimeField] = None) -> str:

        if ts_data is None or ts_data.path == self.THOR_TIMESTAMP_FIELD:
            return "Timestamp of THOR scan execution"
        module = self._get_value_from_json(json_log, self.THOR_MODULE_FIELD)
        time_fields = " ".join([ts.capitalize() for ts in ts_data.path])
        return f'{module} - {time_fields}'

    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        mandatory_fields = [self.THOR_TIMESTAMP_FIELD, self.THOR_MESSAGE_FIELD, self.THOR_MODULE_FIELD]
        flat = {fields[0] for fields in mandatory_fields if len(fields) == 1}
        parents = {fields[0] for fields in mandatory_fields if len(fields) == 2}
        children = {fields[1] for fields in mandatory_fields if len(fields) == 2}

        return {
            key: (
                {subkey: subvalue for subkey, subvalue in value.items() if subkey not in children}
                if key in parents and isinstance(value, dict)
                else value
            )
            for key, value in json_log.items()
            if key not in flat and (key not in parents or isinstance(value, dict))
        }

    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> str:
        thor_timestamp = self._get_value_from_json(json_log, self.THOR_TIMESTAMP_FIELD)
        if thor_timestamp is None:
            error_msg = f"Missing THOR timestamp field: {self.THOR_TIMESTAMP_FIELD}"
            logger.error(error_msg)
            raise TimestampError(error_msg)
        return str(thor_timestamp)

    def _get_value_from_json(self, json_log: Dict[str, Any], mandatory_fields: List[str]) -> Any:
        values: Any = json_log
        for field in mandatory_fields:
            try:
                if isinstance(values, dict):
                    values = values.get(field)
            except KeyError:
                error_msg = f"Field '{field}' not found in THOR data: {values}"
                logger.error(error_msg)
                raise MappingError(error_msg)
        return values

