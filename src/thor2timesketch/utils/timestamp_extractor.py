from thor2timesketch.config.logger import LoggerConfig
from abc import ABC, abstractmethod
logger = LoggerConfig.get_logger(__name__)
from typing import Dict, Any, List
from thor2timesketch.utils.datetime_field import DatetimeField

class TimestampExtractor(ABC):

    @abstractmethod
    def extract(self, data: Dict[str, Any]) -> List[DatetimeField]:
        pass