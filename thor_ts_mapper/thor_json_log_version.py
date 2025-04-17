from typing import Dict, Any, Type
from thor_ts_mapper.exceptions import VersionError
from thor_ts_mapper.thor_mapper_json import THORMapperJson
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper import constants

logger = LoggerConfig.get_logger(__name__)

class THORJSONLogVersionMapper:

    _mapper_log_version: Dict[str, Type["THORMapperJson"]] = {}

    @classmethod
    def log_version(cls, prefix: str):
        def map_log_version(mapper_cls: Type["THORMapperJson"]) -> Type["THORMapperJson"]:
            cls._mapper_log_version[prefix.lower()] = mapper_cls
            return mapper_cls
        return map_log_version

    def get_mapper_for_version(self, json_line: Dict[str, Any]) -> "THORMapperJson":
        version = json_line.get(constants.LOG_VERSION)
        if not isinstance(version, str):
            raise VersionError(f"Invalid or missing log_version: {version}")
        version = version.lower()

        thor_mapper = next(
            (mapper for prefix, mapper in self._mapper_log_version.items() if version.startswith(prefix)),
            None
        )
        if thor_mapper is not None:
            logger.debug(f"Using {thor_mapper.__name__} for version '{version}'")
            return thor_mapper()

        raise VersionError(f"Unsupported log_version: '{version}'")