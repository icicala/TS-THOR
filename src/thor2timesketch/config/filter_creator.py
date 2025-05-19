import os
import yaml
import itertools
from typing import Dict, Any, Iterator
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.constants import DEFAULT_ENCODING, OUTPUT_YAML_FILE, DEFAULT_LEVELS, DEFAULT_FILTER
from thor2timesketch.exceptions import FilterConfigError
from thor2timesketch.input.json_reader import JsonReader
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_json_audit import MapperJsonAudit
from thor2timesketch.mappers.mapper_json_v1 import MapperJsonV1
from thor2timesketch.mappers.mapper_json_v2 import MapperJsonV2

logger = LoggerConfig.get_logger(__name__)


class FilterCreator:
    def __init__(self, input_file: str) -> None:
        self.input_file = input_file
        self.json_reader = JsonReader()
        self.mapper_resolver = JsonLogVersion()

    def generate_yaml_file(self) -> None:
        try:
            events = self.json_reader.get_valid_data(self.input_file)
            first = next(events)
            mapper = self.mapper_resolver.get_mapper_for_version(first)
            if isinstance(mapper, (MapperJsonV1, MapperJsonV2)):
                config = self._build_filters_from_json_thor(first, events)
            elif isinstance(mapper, MapperJsonAudit):
                config = self._load_default_config()
            else:
                raise FilterConfigError(f"Unsupported mapper for version: {mapper.__class__.__name__}")

            self._write_config(config)

        except Exception as e:
            raise FilterConfigError(f"Failed to generate filter configuration: {e}") from e

    def _build_filters_from_json_thor(
        self,
        first: Dict[str, Any],
        json_logs: Iterator[Dict[str, Any]]
    ) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            "filters": {
                "levels": list(DEFAULT_LEVELS),
                "modules": {"include": [], "exclude": []},
                "features": {"include": [], "exclude": []},
            }
        }
        for entry in itertools.chain([first], json_logs):
            message = entry.get("message", "")
            if message.startswith("Selected modules:"):
                config["filters"]["modules"]["include"].extend(self._parse_items("Selected modules:", message))
            elif message.startswith("Deselected modules:"):
                config["filters"]["modules"]["exclude"].extend(self._parse_items("Deselected modules:", message))
            elif message.startswith("Selected features:"):
                config["filters"]["features"]["include"].extend(self._parse_items("Selected features:", message))
            elif message.startswith("Deselected features:"):
                config["filters"]["features"]["exclude"].extend(self._parse_items("Deselected features:", message))
        return config

    def _load_default_config(self) -> Dict[str, Any]:
        try:
            with open(DEFAULT_FILTER, encoding=DEFAULT_ENCODING) as fp:
                return yaml.safe_load(fp) or {"filters": {}}
        except Exception as e:
            raise FilterConfigError(f"Failed to load default filter '{DEFAULT_FILTER}': {e}")

    def _write_config(self, config: Dict[str, Any]) -> None:
        output_file = os.path.join(os.getcwd(), OUTPUT_YAML_FILE)
        logger.info(f"Creating filter configuration at `{output_file}`")
        with open(output_file, "w", encoding=DEFAULT_ENCODING) as file:
            yaml.safe_dump(config, file, sort_keys=False)
        logger.info(f"Filter configuration successfully written to '{output_file}'")

    def _parse_items(self, prefix: str, message: str) -> list[str]:
        modules_features = message[len(prefix):].strip()
        return [item.strip() for item in modules_features.split(",") if item.strip()]