import json
from typing import List, Dict, Any
from thor_ts_mapper.logger_config import LoggerConfig

logger = LoggerConfig.get_logger(__name__)


class THORJSONOutputWriter:


    @staticmethod
    def write_timesketch_data(mapped_data: List[Dict[str, Any]], output_file: str) -> bool:
        try:
            THORJSONOutputWriter._write_json_lines(mapped_data, output_file)
            logger.info(f"Successfully wrote {len(mapped_data)} events to {output_file}")
            return True
        except IOError as e:
            logger.error(f"Error writing to {output_file}: {e}")
            return False



    @staticmethod
    def _write_json_lines(data: List[Dict[str, Any]], output_file: str) -> None:
        with open(output_file, 'w', encoding='utf-8') as file:
            for entry in data:
                file.write(json.dumps(entry) + '\n')