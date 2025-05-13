from typing import Optional
import os
import yaml
from thor2timesketch import constants
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.exceptions import FilterConfigError

logger = LoggerConfig.get_logger(__name__)

class FilterFindings:
    def __init__(self, levels: set[str], modules: set[str]) -> None:
        self._levels = levels
        self._modules = modules
        logger.debug(f"Filter initialized with levels={levels} and modules={modules}")

    @classmethod
    def read_from_yaml(cls, path: Optional[str] = None) -> "FilterFindings":
        path = path or os.path.join(os.path.dirname(__file__), constants.DEFAULT_FILTER)
        if not os.path.isfile(path):
            error_msg = f"Filter config file {path} not found"
            logger.error(error_msg)
            raise FilterConfigError(error_msg)
        try:
            with open(path, encoding=constants.DEFAULT_ENCODING) as file:
                filters = yaml.safe_load(file)
            if not isinstance(filters, dict):
                error_msg = f"Invalid filter config format in {path}"
                logger.error(error_msg)
                raise FilterConfigError(error_msg)
            levels = set(filters.get("levels") or [])
            modules = set(filters.get("modules") or [])
            if not levels and not modules:
                error_msg = f"Empty filter config in {path}: at least one filter (levels or modules) must be provided"
                logger.error(error_msg)
                raise FilterConfigError(error_msg)
            logger.info(f"Filter config loaded from {path}: levels={levels}, modules={modules}")
            return cls(levels=levels, modules=modules)
        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error in config '{path}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error in filter config '{path}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error loading filter config '{path}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e

    def matches_filter_criteria(self, level: Optional[str] = None, module: Optional[str] = None) -> bool:
        level_match = level in self._levels if self._levels else True
        module_match = module in self._modules if self._modules else True
        return level_match and module_match