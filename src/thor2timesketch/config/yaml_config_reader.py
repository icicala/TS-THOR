from thor2timesketch.constants import VALID_YAML_EXTENSIONS, DEFAULT_ENCODING
from thor2timesketch.exceptions import FilterConfigError
from thor2timesketch.input.file_validator import FileValidator
from typing import Dict, Any, Optional
import yaml


class YamlConfigReader:

    @staticmethod
    def load_yaml(config_path: str) -> Dict[str, Any]:

        validator = FileValidator(valid_extensions=VALID_YAML_EXTENSIONS)
        yaml_file = validator.validate_file(config_path)

        try:
            with open(yaml_file, encoding=DEFAULT_ENCODING) as file:
                content = yaml.safe_load(file) or {}
                filters = content.get("filters")
                if not isinstance(filters, dict):
                    error_msg = f"Invalid filter config format in {yaml_file}"
                    logger.error(error_msg)
                    raise FilterConfigError(error_msg)
                return content
        except yaml.YAMLError as e:
            raise FilterConfigError(f"YAML parse error in {yaml_file}: {e}") from e
        except UnicodeDecodeError as e:
            raise FilterConfigError(f"Encoding error in {yaml_file}: {e}") from e
        except Exception as e:
            raise FilterConfigError(f"Unexpected error in {yaml_file}: {e}") from e
