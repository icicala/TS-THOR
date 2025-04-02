from abc import abstractmethod, ABC
from typing import Dict, Any
from mapping_mode import MappingMode


class THORMapperJson(ABC):
    def map_thor_events(self, json_line: Dict[str, Any], mode: MappingMode) -> Dict[str, Any]:
        """Template TS mandatory fields"""
        message = self._get_message(json_line)
        datetime_val = self._get_datetime(json_line, mode)
        timestamp_desc = self._get_timestamp_desc(json_line, mode)
        event = {
            'message': message,
            'datetime': datetime_val,
            'timestamp_desc': timestamp_desc
        }
        if mode == MappingMode.MULTIPLE_TIMESTAMP:
            event['time_thor_scan'] = self._get_datetime(json_line, mode)

        event.update(self._get_additional_fields(json_line, mode))
        return event

    @abstractmethod
    def _get_message(self, json_line: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def _get_datetime(self, json_line: Dict[str, Any], mode) -> str:
        pass

    @abstractmethod
    def _get_timestamp_desc(self, json_line: Dict[str, Any], mode) -> str:
        pass

    @abstractmethod
    def _get_additional_fields(self, json_line: Dict[str, Any], mode) -> Dict[str, Any]:
        pass