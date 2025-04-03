import os
import json
from typing import List, Dict, Any

from thor_ts_mapper.logger_config import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

class THORJSONOutputWriter:
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.mode = 'a' if os.path.exists(output_file) else 'w'
        self.file = None

    def open(self):
        if self.file is None:
            self.file = open(self.output_file, self.mode, encoding='utf-8')
            logger.debug(f"Opened file {self.output_file} in mode {self.mode}")
        return self
    def close(self) -> None:
        if self.file is not None:
            self.file.close()
            self.file = None
            logger.debug(f"Closed file {self.output_file}")

    def write_mapped_logs(self, mapped_logs: List[Dict[str, Any]]) -> None:
        if not mapped_logs:
            return
        if self.file is None:
            self.open()

        try:
            self.file.writelines(json.dumps(entry) + '\n' for entry in mapped_logs)
            self.file.flush()
            logger.info(f"Successfully wrote {len(mapped_logs)} events to {self.output_file}")
        except IOError as e:
            logger.error(f"Error writing to {self.output_file}: {e}")
