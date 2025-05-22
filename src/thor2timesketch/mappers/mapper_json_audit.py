from typing import Dict, Any, List
from abc import abstractmethod
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.utils.audit_timestamp_extractor import AuditTimestampExtractor
from thor2timesketch.utils.normalizer import AuditTrailNormalizer
from thor2timesketch.utils.thor_finding_id import ThorFindingId
from thor2timesketch.utils.datetime_field import DatetimeField


class MapperJsonAudit(MapperJsonBase):

    def __init__(self) -> None:
        super().__init__(
            normalizer=AuditTrailNormalizer(), time_extractor=AuditTimestampExtractor()
        )

    def map_thor_events(self, json_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        all_timestamps = self.timestamp_extractor.extract(json_log)
        normalized = self.normalizer.normalize(json_log)
        event_group_id = ThorFindingId.get_finding_id()
        for index, time_data in enumerate(all_timestamps):
            primary = index == 0
            event = self._create_audit_event(
                normalized, time_data, event_group_id, primary
            )
            events.append(event.to_dict())
        return events

    @abstractmethod
    def _create_audit_event(
        self,
        json_log: Dict[str, Any],
        time_data: DatetimeField,
        event_group_id: str,
        primary: bool,
    ):
        pass
