from typing import Any, Dict
from collections import deque
from thor_ts_mapper import constants
from thor_ts_mapper.exceptions import JsonFlatteningError
from thor_ts_mapper.logger_config import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

class THORJSONFlattener:

    def __init__(self):
        self.delimiter = constants.DELIMITER


    def _index_to_letter(self, index: int) -> str:
        result = ""
        index += 1
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            result = chr(65 + remainder) + result
        return result

    def flatten_jsonl(self, json_line: Dict[str, Any]) -> Dict[str, Any]:
        if json_line is None:
            logger.warning("Received an empty THOR log as input for flattening.")
            return {}
        #bfs algorithm
        flattened: Dict[str, Any] = {}
        queue = deque([(json_line, "")])
        try:
            while queue:
                current, key_path = queue.popleft()

                if isinstance(current, dict):
                    for key, value in current.items():
                        new_key = f"{key_path}{self.delimiter}{key}" if key_path else key
                        queue.append((value, new_key))
                elif isinstance(current, list):
                    for index, item in enumerate(current):
                        alpha_index = self._index_to_letter(index)
                        new_key = f"{key_path}{self.delimiter}{alpha_index}"
                        queue.append((item, new_key))
                else:
                    flattened[key_path] = current
        except Exception as e:
            error_msg = f"Unexpected error during flattening: {str(e)}"
            logger.error(error_msg)
            raise JsonFlatteningError(error_msg)

        logger.debug("Successfully flattened JSON: %s", flattened)
        return flattened