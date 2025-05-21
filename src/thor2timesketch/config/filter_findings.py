from typing import Optional
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.config.yaml_config_reader import YamlConfigReader
from thor2timesketch.exceptions import FilterConfigError


logger = LoggerConfig.get_logger(__name__)

class FilterFindings:
    def __init__(self, levels: set[str], modules: set[str]) -> None:
        self._levels = {level.lower() for level in levels}
        self._modules = {module.lower() for module in modules}
        logger.debug(f"Filter initialized with levels={levels}, modules={modules}")

    @classmethod
    def read_filters_yaml(cls, config_filter: Optional[str] = None) -> "FilterFindings":

        if config_filter is None:
            return cls.null_filter()

        filter_file = YamlConfigReader.load_yaml(config_filter)

        filter_section = filter_file.get("filters")
        if not filter_section:
            error_msg = f"Missing 'filters' section in filter config {filter_file}"
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
            error_msg = f"Empty filter config in {filter_file}: at least one filter include (levels or modules) must be provided"
            logger.error(error_msg)
            raise FilterConfigError(error_msg)
        logger.info(f"Filter config loaded from {filter_file}: levels={levels}, modules={modules_final}")
        return cls(levels, modules_final)

    @classmethod
    def null_filter(cls) -> "FilterFindings":
        no_filter = cls(set(), set())
        no_filter.matches_filter_criteria = lambda level, module: True
        return no_filter

    def matches_filter_criteria(self, level: Optional[str], module: Optional[str]) -> bool:
        norm_level = level.lower() if level is not None else None
        norm_module = module.lower() if module is not None else None
        if self._levels and not self._modules:
            return norm_level in self._levels
        if self._modules and not self._levels:
            return norm_module in self._modules
        return norm_level in self._levels and norm_module in self._modules