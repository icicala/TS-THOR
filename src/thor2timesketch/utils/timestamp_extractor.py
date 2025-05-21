from thor2timesketch.config.logger import LoggerConfig
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dateutil import parser
from thor2timesketch.exceptions import MappingError
from thor2timesketch.utils.datetime_field import DatetimeField

logger = LoggerConfig.get_logger(__name__)


class TimestampExtractor(ABC):
    def is_same_timestamp(self, time1: str, time2: str) -> bool:
        try:
            datetime1 = parser.isoparse(time1)
            datetime2 = parser.isoparse(time2)
            ts_check = datetime1 == datetime2
            return ts_check
        except ValueError as e:
            error_msg = f"Error parsing timestamps: {e}"
            logger.error(error_msg)
            raise MappingError(error_msg)

    @abstractmethod
    def extract(self, data: Dict[str, Any]) -> List[DatetimeField]:
        pass
