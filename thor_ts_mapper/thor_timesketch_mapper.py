import re
from thor_ts_mapper.logger_config import LoggerConfig
from datetime import timezone
from typing import Dict, List, Any
from thor_ts_mapper.event_category import EventCategory
from dateutil import parser

logger = LoggerConfig.get_logger(__name__)


class ThorTimesketchMapper:

    ISO8601_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?$)', re.IGNORECASE) # ISO 8601 format
    MULTIPLE_DATETIME_THRESHOLD = 1

    METADATA_MODULES = {"Startup", "Init", "Yara", "Sigma", "ThorDB", "Report", "EtwWatcher"}
    METADATA_MESSAGES = {"Starting module", "Finished module"}

    @staticmethod
    def extract_datetime(thor_json_line: Dict[str, Any]) -> Dict[str, str]:
        # dfs for extracting datetimes
        datetime_thor: Dict[str, str] = {}
        stack = [(thor_json_line, "")]

        while stack:
            obj, key_path = stack.pop()

            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{key_path}.{key}" if key_path else key
                    stack.append((value, new_key))
            elif isinstance(obj, list):
                for index, item in enumerate(obj):
                    new_key = f"{key_path}_{index}"
                    stack.append((item, new_key))
            elif isinstance(obj, str) and ThorTimesketchMapper.ISO8601_PATTERN.match(obj):
                try:
                    timestamp = parser.isoparse(obj)
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                    datetime_thor[key_path] = timestamp.isoformat()
                except ValueError:
                    logger.warning(f"Invalid datetime format at {key_path}: {obj}")

        return datetime_thor

    @staticmethod
    def _determine_category(thor_json_line: Dict[str, Any], timestamps_extract: Dict[str, str]) -> str:
        module = thor_json_line.get("module")
        message = thor_json_line.get("message")

        is_metadata = (
            module in ThorTimesketchMapper.METADATA_MODULES or
            message in ThorTimesketchMapper.METADATA_MESSAGES
        )

        if is_metadata:
            return EventCategory.THOR_SCAN_METADATA.value
        elif len(timestamps_extract) > ThorTimesketchMapper.MULTIPLE_DATETIME_THRESHOLD:
            return EventCategory.MODULE_TIMESTAMP.value
        else:
            return EventCategory.SINGLE_TIMESTAMP.value

    @staticmethod
    def map_and_categorize(thor_json_line: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:

        categorized: Dict[str, List[Dict[str, Any]]] = {}
        events: List[Dict[str, Any]] = []

        timestamps_extract = ThorTimesketchMapper.extract_datetime(thor_json_line)
        category = ThorTimesketchMapper._determine_category(thor_json_line, timestamps_extract)
        thor_scan_time = timestamps_extract.pop("time", None)
        message = thor_json_line.get("message")
        module = thor_json_line.get("module")



        if timestamps_extract:
            for key, timestamp in timestamps_extract.items():
                event = {
                    "datetime": timestamp,
                    "message": message,
                    "timestamp_desc": f'{module} - {key}',
                    "thor_scan_time": thor_scan_time
                }
                event.update({
                    field: value for field, value in thor_json_line.items()
                    if field not in ["message", "time", key]
                })
                events.append(event)
        else:
            event = {
                "datetime": thor_scan_time,
                "message": message,
                "timestamp_desc": "Timestamp of THOR scan execution"
            }
            event.update({
                field: value for field, value in thor_json_line.items()
                if field not in ["message", "time"]
            })
            events.append(event)

        categorized[category] = events
        return categorized