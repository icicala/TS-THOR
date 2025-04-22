from src.thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from src.thor2timesketch.mappers.json_log_version import JsonLogVersion

@JsonLogVersion.log_version("v3.0.0")
class MapperJsonV3(MapperJsonBase):

    THOR_TIMESTAMP_FIELD = "meta_time"
    THOR_MESSAGE_FIELD = "summary"
    THOR_MODULE_FIELD = "meta_module"