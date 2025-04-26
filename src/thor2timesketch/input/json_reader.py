from typing import Iterator, Dict, Any
from thor2timesketch import constants
from thor2timesketch.exceptions import FileValidationError, JsonValidationError, InputError, JsonParseError
from thor2timesketch.input.file_validator import FileValidator
from thor2timesketch.input.json_validator import JsonValidator
from thor2timesketch.config.logger import LoggerConfig


logger = LoggerConfig.get_logger(__name__)

class JsonReader:

    def __init__(self) -> None:
        self.file_validator = FileValidator()
        self.json_validator = JsonValidator()
        self.file_encoder = constants.DEFAULT_ENCODING



    def _validate_file(self,input_file: str) -> str:
        try:
            valid_file: str = self.file_validator.validate_file(input_file)
        except FileValidationError as e:
            message_err = f"File validation error: {e}"
            logger.error(message_err)
            raise FileValidationError(message_err)
        return valid_file

    def get_valid_data(self, input_file: str) -> Iterator[Dict[str, Any]]:
        valid_file = self._validate_file(input_file)
        return self._generate_valid_json(valid_file)

    def _generate_valid_json(self, valid_file: str) -> Iterator[Dict[str, Any]]:
        try:
            with open(valid_file, 'r', encoding=self.file_encoder) as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        json_data = self.json_validator.validate_json_log(line)
                        if json_data is not None:
                            yield json_data
                    except (JsonParseError, JsonValidationError) as e:
                        logger.error(f"Error parsing JSON at line {line_num}: {e}")
                        raise
        except IOError as e:
            message_err = f"Error opening or reading file: {e}"
            logger.error(message_err)
            raise InputError(message_err)