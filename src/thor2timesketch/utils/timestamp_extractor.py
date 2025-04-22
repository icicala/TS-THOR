import re
from typing import Dict, Any, List
from src.thor2timesketch import constants
from src.thor2timesketch.config.logger import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

class TimestampExtractor:

    def __init__(self) -> None:
        self.ISO8601 = re.compile(constants.ISO8601_PATTERN, re.IGNORECASE)


    def extract_datetime(self, thor_json_line: Dict[str, Any]) -> List[str]:
        timestamp_fields: List[str] = []

        for field, value in thor_json_line.items():
            if isinstance(value, str) and self.ISO8601.match(value):
                timestamp_fields.append(field)
        has_multiple_timestamps = len(timestamp_fields) > 1
        if has_multiple_timestamps:
            logger.debug(f"Multiple timestamp fields found: {timestamp_fields}")
        else:
            logger.debug(f"THOR timestamp field found only: {timestamp_fields}")
        return timestamp_fields