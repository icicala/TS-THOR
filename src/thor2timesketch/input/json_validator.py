import json
from typing import Dict, Any, Optional
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.exceptions import JsonValidationError, JsonParseError

class JsonValidator:

    def validate_json_log(self, json_log: str) -> Optional[Dict[str, Any]]:
        if not json_log.strip():
            return None
        json_obj = self._parse_json_log(json_log)
        valid_json = self._validate_json_log(json_obj)
        return valid_json

    def _parse_json_log(self, json_log: str) -> Dict[str, Any]:
        try:
            return json.loads(json_log)
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {str(e)}"
            ConsoleConfig.error(error_msg)
            raise JsonParseError(error_msg)

    def _validate_json_log(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(json_log, dict):
            error_msg = "Not a valid JSON object: Expected a dictionary."
            ConsoleConfig.error(error_msg)
            raise JsonValidationError(error_msg)
        return json_log
