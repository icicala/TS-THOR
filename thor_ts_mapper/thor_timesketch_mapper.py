import re
from thor_ts_mapper.logger_config import LoggerConfig
from datetime import timezone
from typing import Dict, List, Any

from dateutil import parser

logger = LoggerConfig.get_logger(__name__)


class ThorTimesketchMapper:


    @staticmethod
    def map_and_categorize(thor_json_line: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:

        categorized: Dict[str, List[Dict[str, Any]]] = {}
        events: List[Dict[str, Any]] = []

        timestamps_extract = ThorTimesketchMapper._extract_datetime(thor_json_line)
        thor_scan_time = timestamps_extract.pop("time", None)
        message = thor_json_line.get("message")
        module = thor_json_line.get("module")



        if timestamps_extract:
            for key, timestamp in timestamps_extract.items():
                event = {
                    "datetime": timestamp,
                    "message": message,
                    "timestamp_desc": f'{module} - {key}',
                    "time_thor_scan": thor_scan_time
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

        categorized["TBD"] = events
        return categorized