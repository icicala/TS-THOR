from thor2timesketch.utils.timestamp_extractor import TimestampExtractor
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.utils.audit_timestamp_extractor import AuditTimestampExtractor
from thor2timesketch.utils.normalizer import AuditTrailNormalizer
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase

class MapperJsonAudit(MapperJsonBase):
    def __init__(self) -> None:
        super().__init__(
            normalizer=AuditTrailNormalizer(),
            ts_strategy=DictTimestampStrategy()
        )