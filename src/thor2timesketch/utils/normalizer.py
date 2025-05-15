from abc import ABC, abstractmethod
from typing import Dict, Any
from thor2timesketch.utils.json_flattener import JSONFlattener
from thor2timesketch.config.logger import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

class JsonNormalizer(ABC):
    @abstractmethod
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class IdentityNormalizer(JsonNormalizer):
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("Using identity normalizer (no flattening)")
        return data

class FlatteningNormalizer(JsonNormalizer):
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("Using flattening normalizer")
        return JSONFlattener.flatten_json(data)

class AuditTrailNormalizer(JsonNormalizer):
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        details = data.pop("Details", {})
        if not isinstance(details, dict) or not details:
            return data
        for key, value in details.items():
            field = key if key not in data else f"Details_{key}"
            data[field] = value
        timestamps = data.pop("Timestamps", {})
        flatten_json = JSONFlattener.flatten_json(data)
        flatten_json["Timestamps"] = timestamps
        return flatten_json