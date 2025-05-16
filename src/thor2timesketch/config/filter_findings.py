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
    def read_from_yaml(cls, config_filter: Optional[str] = None) -> "FilterFindings":
        default_filter_path = os.path.join(os.path.dirname(__file__), constants.DEFAULT_FILTER)
        filter_path = config_filter or default_filter_path
        if not os.path.isfile(filter_path):
            error_msg = f"Filter config file {filter_path} not found"
            logger.error(error_msg)
            raise FilterConfigError(error_msg)
        try:
            with open(filter_path, encoding=constants.DEFAULT_ENCODING) as file:
                filters = yaml.safe_load(file)
            if not isinstance(filters, dict):
                error_msg = f"Invalid filter config format in {filter_path}"
                logger.error(error_msg)
                raise FilterConfigError(error_msg)
            levels = {level.lower() for level in filters.get("levels") or []}
            modules = {module.lower() for module in filters.get("modules") or []}
            if not levels and not modules:
                error_msg = f"Empty filter config in {filter_path}: at least one filter (levels or modules) must be provided"
                logger.error(error_msg)
                raise FilterConfigError(error_msg)
            logger.info(f"Filter config loaded from {filter_path}: levels={levels}, modules={modules}")
            return cls(levels, modules)
        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error in config '{filter_path}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error in filter config '{filter_path}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error loading filter config '{filter_path}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e

    def matches_filter_criteria(self, level: Optional[str], module: Optional[str]) -> bool:
        norm_level = level.lower() if level is not None else None
        norm_module = module.lower() if module is not None else None
        if self._levels and not self._modules:
            return norm_level in self._levels
        if self._modules and not self._levels:
            return norm_module in self._modules
        return norm_level in self._levels and norm_module in self._modules