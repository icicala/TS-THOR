from thor2timesketch.constants import VALID_YAML_EXTENSIONS, DEFAULT_ENCODING
from thor2timesketch.exceptions import FilterConfigError, FileValidationError
from thor2timesketch.input.file_validator import FileValidator
from typing import Dict, Any
import yaml
from thor2timesketch.config.console_config import ConsoleConfig
from pathlib import Path


class YamlConfigReader:

    @staticmethod
    def load_yaml(config_path: Path) -> Dict[str, Any]:
        try:
            validator = FileValidator(valid_extensions=VALID_YAML_EXTENSIONS)
            yaml_file = validator.validate_file(config_path)
        except FileValidationError as e:
            error_msg = f"Invalid YAML file `{config_path}`: {e}"
            ConsoleConfig.error(error_msg)
            raise FilterConfigError(error_msg) from e
        try:
            with yaml_file.open("r", encoding=DEFAULT_ENCODING) as file:
                content = yaml.safe_load(file) or {}
        except yaml.YAMLError as e:
            error_msg = f"YAML parse error in {yaml_file}: {e}"
            ConsoleConfig.error(error_msg)
            raise FilterConfigError(error_msg) from e
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error in {yaml_file}: {e}"
            ConsoleConfig.error(error_msg)
            raise FilterConfigError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error in {yaml_file}: {e}"
            ConsoleConfig.error(error_msg)
            raise FilterConfigError(error_msg) from e

        filters = content.get("filters")
        if not isinstance(filters, dict):
            error_msg = f"Invalid filter config format in {yaml_file}"
            ConsoleConfig.error(error_msg)
            raise FilterConfigError(error_msg)
        return filters
