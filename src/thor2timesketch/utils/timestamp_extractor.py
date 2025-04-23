import re
from collections import deque
from datetime import timezone
from typing import Dict, Any, List, Tuple
from dateutil import parser
from src.thor2timesketch import constants
from src.thor2timesketch.config.logger import LoggerConfig
from src.thor2timesketch.exceptions import TimestampError
from src.thor2timesketch.utils.datetime_field import DatetimeField

logger = LoggerConfig.get_logger(__name__)

class TimestampExtractor:

    def __init__(self) -> None:
        self.ISO8601 = re.compile(constants.ISO8601_PATTERN, re.IGNORECASE)

    def extract_datetime(self, data_json: Dict[str, Any]) -> List[DatetimeField]:

        if data_json is None:
            error_msg = "Received an empty THOR log as input for timestamp extractor."
            logger.error(error_msg)
            raise TimestampError(error_msg)

        timestamps: List[DatetimeField] = []
        queue: deque[Tuple[Dict[str, Any], List[str]]] = deque([(data_json, [])])

        try:
            while queue:
                log_json, path = queue.popleft()

                if isinstance(log_json, dict):
                    for log_field, log_value in log_json.items():
                        new_path = path + [log_field]
                        queue.append((log_value, new_path))
                elif isinstance(log_json, list):
                    for log_value in log_json:
                        queue.append((log_value, path))
                else:
                    if isinstance(log_json, str) and self.ISO8601.match(log_json):
                        try:
                            parsed_date = parser.isoparse(log_json)
                            if parsed_date.tzinfo is None:
                                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                            iso_data = parsed_date.isoformat()
                            logger.debug(f"Found ISO8601 date {iso_data} at path {path}")
                            timestamps.append(DatetimeField(path=path, datetime=iso_data))
                        except (ValueError, TypeError)  as e:
                            error_msg = f"Error parsing date '{log_json}' at path '{path}': {str(e)}"
                            logger.error(error_msg)
                            raise TimestampError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during timestamp extraction: {str(e)}"
            logger.error(error_msg)
            raise TimestampError(error_msg)

        return timestamps