from typing import Dict, Any, Type
from thor_ts_mapper.exceptions import VersionError
from thor_ts_mapper.thor_mapper_json import THORMapperJson
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper import constants

logger = LoggerConfig.get_logger(__name__)

class THORJSONLogVersionMapper:

    _mapper_log_version: Dict[str, Type["THORMapperJson"]] = {}

    @classmethod
    def log_version(cls, log_version: str):
        def map_log_version(mapper_cls: Type["THORMapperJson"]) -> Type["THORMapperJson"]:
            cls._mapper_log_version[log_version.lower()] = mapper_cls
            logger.debug(f"Mapping log version {log_version} to {mapper_cls}")
            return mapper_cls
        return map_log_version

    def get_mapper_for_version(self, json_line: Dict[str, Any]) -> "THORMapperJson":
        thor_version = json_line.get(constants.LOG_VERSION)
        if not isinstance(thor_version, str):
            raise VersionError(f"Invalid or missing log_version: {thor_version}")
        thor_version = thor_version.lower()

        thor_mapper = next((mapper for version, mapper in self._mapper_log_version.items() if thor_version == version), None)
        if thor_mapper is None:
            raise VersionError(f'The mapper for version "{thor_version}" is not implemented')
        logger.debug(f"Using {thor_mapper.__name__} for version '{thor_version}'")
        return thor_mapper()
