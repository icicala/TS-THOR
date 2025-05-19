from typing import Optional
import yaml
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.exceptions import FilterConfigError
from thor2timesketch.input.file_validator import FileValidator
from thor2timesketch.constants import VALID_YAML_EXTENSIONS, DEFAULT_ENCODING

logger = LoggerConfig.get_logger(__name__)

class FilterFindings:
    def __init__(self, levels: set[str], modules: set[str]) -> None:
        self._levels = levels
        self._modules = modules
        logger.debug(f"Filter initialized with levels={levels}, modules={modules}")

    @classmethod
    def read_from_yaml(cls, config_filter: Optional[str] = None) -> "FilterFindings":

        if config_filter is None:
            return cls.null_filter()

        file_yaml_validator = FileValidator(valid_extensions=VALID_YAML_EXTENSIONS)
        valid_yaml_file = file_yaml_validator.validate_file(config_filter)
        try:
            valid_yaml_file = file_yaml_validator.validate_file(config_filter)
            with open(valid_yaml_file, encoding=DEFAULT_ENCODING) as file:
                filters = yaml.safe_load(file)
            if not isinstance(filters, dict):
                error_msg = f"Invalid filter config format in {valid_yaml_file}"
                logger.error(error_msg)
                raise FilterConfigError(error_msg)

            filter_section = filters.get("filters")
            if not filter_section:
                error_msg = f"Missing 'filters' section in filter config {valid_yaml_file}"
                logger.error(error_msg)
                raise FilterConfigError(error_msg)
            levels = {level.lower() for level in filter_section.get("levels") or {} if isinstance(level, str)}
            modules_include = {module.lower() for module in filter_section.get("modules").get("include") or {} if isinstance(module, str)}
            modules_exclude = {module.lower() for module in filter_section.get("modules").get("exclude") or {} if isinstance(module, str)}

            features_include = {feature.lower() for feature in filter_section.get("features").get("include") or {} if isinstance(feature, str)}
            features_exclude = {feature.lower() for feature in filter_section.get("features").get("exclude") or {} if isinstance(feature, str)}

            modules_filtered = modules_include - modules_exclude
            features_filtered = features_include - features_exclude
            modules_final = modules_filtered | features_filtered

            if not levels and not modules_final:
                error_msg = f"Empty filter config in {valid_yaml_file}: at least one filter include (levels or modules) must be provided"
                logger.error(error_msg)
                raise FilterConfigError(error_msg)
            logger.info(f"Filter config loaded from {valid_yaml_file}: levels={levels}, modules={modules_final}")
            return cls(levels, modules_final)
        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error in config '{valid_yaml_file}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error in filter config '{valid_yaml_file}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error loading filter config '{valid_yaml_file}': {e}"
            logger.error(error_msg)
            raise FilterConfigError(error_msg) from e

    @classmethod
    def null_filter(cls) -> "FilterFindings":
        no_filter = cls(set(), set())
        no_filter.matches_filter_criteria = lambda level, module: True  # type: ignore
        return no_filter

    def matches_filter_criteria(self, level: Optional[str], module: Optional[str]) -> bool:
        norm_level = level.lower() if level is not None else None
        norm_module = module.lower() if module is not None else None
        if self._levels and not self._modules:
            return norm_level in self._levels
        if self._modules and not self._levels:
            return norm_module in self._modules
        return norm_level in self._levels and norm_module in self._modules