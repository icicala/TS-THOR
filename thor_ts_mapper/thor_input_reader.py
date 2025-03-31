
from typing import List, Dict, Tuple, Optional
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.exceptions import FileValidationError, JsonValidationError
from thor_ts_mapper.file_validator import FileValidator
from thor_ts_mapper.json_line_validator import JSONLineValidator

logger = LoggerConfig.get_logger(__name__)


class THORJSONInputReader:

    @staticmethod
    def _validate_file(input_file: str) -> bool:
        try:
            FileValidator.validate_file(input_file)
            return True
        except FileValidationError as e:
            logger.error("File validation error: %s", e)
            return False

    @staticmethod
    def _extract_valid_json(input_file: str) -> List[Dict]:
        valid_entries = []

        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        is_valid, json_data = JSONLineValidator.validate_json(line)
                        if is_valid and json_data is not None:
                            valid_entries.append(json_data)
                    except JsonValidationError as e:
                        logger.error(f"Invalid JSON at line {line_num}: {e}")
        except IOError as e:
            logger.error(f"Error opening or reading file: {e}")
            return []

        return valid_entries

    @staticmethod
    def read_file(input_file: str) -> Tuple[bool, Optional[List[Dict]]]:

        if not THORJSONInputReader._validate_file(input_file):
            return False, None

        valid_entries = THORJSONInputReader._extract_valid_json(input_file)

        if not valid_entries:
            logger.error(f"No valid JSON entries found in {input_file}.")
            return False, None

        logger.info(f"Successfully read {len(valid_entries)} valid entries from {input_file}.")
        return True, valid_entries


