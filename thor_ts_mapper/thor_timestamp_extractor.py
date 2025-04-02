import re
from typing import Dict, Any
from dateutil import parser
from datetime import timezone

from thor_ts_mapper.logger_config import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

class ThorTimestampExtractor:
    ISO8601_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?$)', re.IGNORECASE) # ISO 8601 format

    @staticmethod
    def _extract_datetime(thor_json_line: Dict[str, Any]) -> Dict[str, str]:
        datetime_thor: Dict[str, str] = {}

        for key, value in thor_json_line.items():
            if isinstance(value, str) and ThorTimestampExtractor.ISO8601_PATTERN.match(value):
                try:
                    timestamp = parser.isoparse(value)
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                    datetime_thor[key] = timestamp.isoformat()
                except ValueError:
                    logger.warning(f"Invalid datetime format at {key}: {value}")

        return datetime_thor