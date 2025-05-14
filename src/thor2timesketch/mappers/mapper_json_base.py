from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.mappers.mapped_event import MappedEvent
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.utils.timestamp_extractor import TimestampExtractor
from thor2timesketch.utils.thor_finding_id import ThorFindingId

logger = LoggerConfig.get_logger(__name__)


class MapperJsonBase(ABC):
    THOR_TIMESTAMP_FIELD: str = ""
    THOR_MESSAGE_FIELD: str = ""
    THOR_MODULE_FIELD: str = ""
    THOR_LEVEL_FIELD: str = ""

    def __init__(self) -> None:
        self.timestamp_extractor: TimestampExtractor = TimestampExtractor()

    def map_thor_events(self, json_log: Dict[str, Any]) -> List[Dict[str, Any]]:

        logger.debug("Starting to map THOR events")
        events: List[Dict[str, Any]] = []

        ref_id = ThorFindingId.get_finding_id()

        thor_timestamp = self._get_thor_timestamp(json_log)
        thor_event = self._create_thor_event(json_log, ref_id)
        events.append(thor_event.to_dict())

        all_timestamps: List[DatetimeField] = self._get_timestamp_extract(json_log)
        additional_timestamp = [ts for ts in all_timestamps if not self.timestamp_extractor.is_same_timestamp(ts.datetime, thor_timestamp.datetime) and ts.path != thor_timestamp.path]

        if additional_timestamp:
            logger.debug(f"Found {len(additional_timestamp)} additional timestamps")
            for timestamp in additional_timestamp:
                event = self._create_additional_timestamp_event(json_log, timestamp, ref_id)
                events.append(event.to_dict())

        logger.debug(f"Mapped {len(events)} events")
        return events

    def _create_thor_event(self, json_log: Dict[str, Any], ref_id: str) -> MappedEvent:
        event = MappedEvent(
            message = self._get_message(json_log),
            datetime = self._get_thor_timestamp(json_log).datetime,
            timestamp_desc = self._get_timestamp_desc(json_log),
            ref_id = ref_id,
            tags = self._get_thor_tags(json_log)
        )

        event.add_additional(self._get_additional_fields(json_log))
        return event


    def _create_additional_timestamp_event(self, json_log: Dict[str, Any],
                                           ts_data: DatetimeField, ref_id: str) -> MappedEvent:
        event = MappedEvent(
            message = self._get_message(json_log),
            datetime = ts_data.datetime,
            timestamp_desc = self._get_timestamp_desc(json_log, ts_data),
            ref_id = ref_id,
            tags = self._get_additional_tags(json_log))
        return event

    def _get_timestamp_extract(self, json_log: Dict[str, Any]) -> List[DatetimeField]:
        ts_extractor: List[DatetimeField] = self.timestamp_extractor.extract_datetime(json_log)
        return ts_extractor

    @abstractmethod
    def _get_message(self, json_log: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def _get_timestamp_desc(self, json_log: Dict[str, Any], ts_data: Optional[DatetimeField] = None) -> str:
        pass

    @abstractmethod
    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        pass
    @abstractmethod
    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> DatetimeField:
        pass

    @abstractmethod
    def get_filterable_fields(self, json_log: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        pass

    @abstractmethod
    def _get_thor_tags(self, json_log: Dict[str, Any]) -> List[str]:
        pass

    @abstractmethod
    def _get_additional_tags(self, json_log: Dict[str, Any]) -> List[str]:
        pass
