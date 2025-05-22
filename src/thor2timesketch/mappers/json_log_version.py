from typing import Dict, Any, Type, Callable
from thor2timesketch.constants import LOG_VERSION, AUDIT_FINDING, AUDIT_INFO
from thor2timesketch.exceptions import VersionError
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.config.logger import LoggerConfig

logger = LoggerConfig.get_logger(__name__)


class JsonLogVersion:

    _mapper_log_version: Dict[str, Type["MapperJsonBase"]] = {}

    @classmethod
    def log_version(
        cls, log_version: str
    ) -> Callable[[Type["MapperJsonBase"]], Type["MapperJsonBase"]]:
        def map_log_version(
            mapper_cls: Type["MapperJsonBase"],
        ) -> Type["MapperJsonBase"]:
            cls._mapper_log_version[log_version.lower()] = mapper_cls
            logger.debug(f"Mapping log version {log_version} to {mapper_cls}")
            return mapper_cls

        return map_log_version

    def detect_log_version(self, json_line: Dict[str, Any]) -> str:
        if LOG_VERSION in json_line:
            log_version = json_line[LOG_VERSION]
            if not isinstance(log_version, str):
                raise VersionError(f"Invalid '{LOG_VERSION}' type: {log_version!r}")
            return log_version.lower()
        if (
            isinstance(json_line, dict)
            and "Module" in json_line
            and "Level" in json_line
        ):
            return AUDIT_FINDING
        if isinstance(json_line, dict) and "Name" in json_line and "Id" in json_line:
            return AUDIT_INFO
        raise VersionError(f"Cannot detect log version")

    def get_mapper_for_version(self, json_line: Dict[str, Any]) -> MapperJsonBase:
        version_key = self.detect_log_version(json_line)
        return self._resolve_mapper(version_key)

    def _resolve_mapper(self, log_version: str) -> MapperJsonBase:
        mapper_type = self._mapper_log_version.get(log_version)
        if not mapper_type:
            raise VersionError(f"No mapper registered for version: {log_version!r}")
        return mapper_type()

    # def get_mapper_for_version(self, json_line: Dict[str, Any]) -> "MapperJsonBase":
    #     log_version = None
    #     if LOG_VERSION in json_line:
    #         log_version = json_line.get(LOG_VERSION)
    #         if not isinstance(log_version, str):
    #             raise VersionError(f"Invalid '{LOG_VERSION}' type: {log_version!r}")
    #     elif AUDIT_INFO in json_line and isinstance(json_line[AUDIT_INFO], dict):
    #         log_version = AUDIT_INFO
    #     elif AUDIT_FINDING in json_line and isinstance(json_line[AUDIT_FINDING], list):
    #         log_version = AUDIT_FINDING
    #     if log_version is None:
    #         raise VersionError(f"Could not determine log version: missing '{LOG_VERSION}', 'info' or 'findings'")
    #     thor_mapper = self._mapper_log_version.get(log_version.lower())
    #     if thor_mapper is None:
    #         raise VersionError(f"Unsupported mapper for: {log_version}")
    #     return thor_mapper()
