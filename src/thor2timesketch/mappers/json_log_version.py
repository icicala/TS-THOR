from typing import Dict, Any, Type, Callable
from thor2timesketch.constants import AUDIT_TRAIL, LOG_VERSION, AUDIT_TIMESTAMP
from thor2timesketch.exceptions import VersionError
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.config.logger import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

class JsonLogVersion:

    _mapper_log_version: Dict[str, Type["MapperJsonBase"]] = {}

    @classmethod
    def log_version(cls, log_version: str) -> Callable[[Type["MapperJsonBase"]], Type["MapperJsonBase"]]:
        def map_log_version(mapper_cls: Type["MapperJsonBase"]) -> Type["MapperJsonBase"]:
            cls._mapper_log_version[log_version.lower()] = mapper_cls
            logger.debug(f"Mapping log version {log_version} to {mapper_cls}")
            return mapper_cls
        return map_log_version

    def get_mapper_for_version(self, json_line: Dict[str, Any]) -> "MapperJsonBase":
        thor_version = json_line.get(LOG_VERSION)
        if thor_version is None:
            if AUDIT_TIMESTAMP in json_line:
                thor_version = AUDIT_TRAIL
            else:
                raise VersionError(f"Missing '{LOG_VERSION}' and no audit timestamps found")
        if not isinstance(thor_version, str):
            raise VersionError(f"Invalid '{LOG_VERSION}' type: {thor_version!r}")
        thor_mapper = self._mapper_log_version.get(thor_version.lower())
        if thor_mapper is None:
            raise VersionError(f"Unsupported log version: {thor_version}")
        return thor_mapper()

