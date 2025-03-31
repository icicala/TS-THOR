from enum import Enum


class EventCategory(Enum):
    THOR_SCAN_METADATA = "THOR_scan_metadata"
    MODULE_TIMESTAMP = "Module_timestamp"
    SINGLE_TIMESTAMP = "THOR_timestamp"

    @classmethod
    def get_output_filename(cls, category):
        mapping = {
            cls.THOR_SCAN_METADATA: "THOR_metadata.jsonl",
            cls.MODULE_TIMESTAMP: "THOR_multi_timestamp.jsonl",
            cls.SINGLE_TIMESTAMP: "THOR_single_timestamp.jsonl",
        }
        return mapping.get(category)