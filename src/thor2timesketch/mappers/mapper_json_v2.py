from src.thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from src.thor2timesketch.mappers.json_log_version import JsonLogVersion

@JsonLogVersion.log_version("v1.0.0")
class MapperJsonV2(MapperJsonBase):

    THOR_TIMESTAMP_FIELD = ["time"]
    THOR_MESSAGE_FIELD = ["message"]
    THOR_MODULE_FIELD = ["module"]
