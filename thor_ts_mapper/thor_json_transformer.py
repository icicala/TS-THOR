import os
from typing import Generator

from tqdm import tqdm

from thor_ts_mapper.thor_input_reader import THORJSONInputReader
from thor_ts_mapper.thor_json_flattener import THORJSONFlattener
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.thor_json_log_version import THORJSONLogVersionMapper

logger = LoggerConfig.get_logger(__name__)

class THORJSONTransformer:

    @staticmethod
    def transform_thor_logs(input_file:str) -> Generator[dict, None, None]:
        valid_thor_logs = THORJSONInputReader.get_valid_json(input_file)
        if valid_thor_logs is None:
            logger.error("No valid thor logs found")
            raise Exception("No valid thor logs found")
        def generate_mapped_logs():
            events_transformed = 0
            file_size = os.path.getsize(input_file)
            logger.info(f"Processing input file: {input_file} ({file_size / 1024:.2f} KB)")
            with tqdm(unit=' event', desc='Mapping THOR logs', total=None) as pbar:
                for json_line in valid_thor_logs:
                    try:
                        flattened_json = THORJSONFlattener.flatten_jsonl(json_line)
                        mapper = THORJSONLogVersionMapper.get_mapper(flattened_json)
                        mapped_events = mapper.map_thor_events(flattened_json)
                        pbar.update(1)
                        for event in mapped_events:
                            yield event
                            events_transformed += 1
                            pbar.set_postfix({"mapped": events_transformed})
                    except Exception as e:
                        logger.error(f"Error processing THOR log: {e}")
                        raise
            logger.debug("Finished transforming THOR logs")
        return generate_mapped_logs()
