from typing import Iterator, Dict, Any
from thor2timesketch.exceptions import JsonValidationError, InputError, JsonParseError
from thor2timesketch.input.file_validator import FileValidator
from thor2timesketch.input.json_validator import JsonValidator
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.constants import VALID_JSON_EXTENSIONS, DEFAULT_ENCODING


logger = LoggerConfig.get_logger(__name__)


class JsonReader:

    def __init__(self) -> None:
        self.file_validator = FileValidator(VALID_JSON_EXTENSIONS)
        self.json_validator = JsonValidator()

    def _validate_file(self, input_file: str) -> str:
        valid_file: str = self.file_validator.validate_file(input_file)
        return valid_file

    def get_valid_data(self, input_file: str) -> Iterator[Dict[str, Any]]:
        valid_file = self._validate_file(input_file)
        logger.debug("JSON file validated successfully")
        return self._generate_valid_json(valid_file)

    def _generate_valid_json(self, valid_file: str) -> Iterator[Dict[str, Any]]:
        try:
            with open(valid_file, "r", encoding=DEFAULT_ENCODING) as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        json_data = self.json_validator.validate_json_log(line)
                        if json_data is not None:
                            yield json_data
                    except (JsonParseError, JsonValidationError) as error:
                        logger.error(f"Error parsing JSON at line {line_num}: {error}")
                        raise
        except IOError as error:
            message_err = f"Error opening or reading file '{valid_file}': {error}"
            logger.error(message_err)
            raise InputError(message_err) from error
