# python
import argparse
import json
import os
import logging
from typing import Dict

from thor_ts_mapper.thor_input_reader import THORJSONInputReader
from thor_ts_mapper.thor_json_flattener import JSONFlattener
from thor_ts_mapper.thor_json_log_version import THORJSONLogVersionMapper
from thor_ts_mapper.thor_output_writer import THORJSONOutputWriter
from thor_ts_mapper.logger_config import LoggerConfig


logger = LoggerConfig.get_logger(__name__)



class MainControllerCLI:
    @staticmethod
    def parse_arguments() -> Dict[str, str]:
        parser = argparse.ArgumentParser(
            description="THOR-TS-Mapper converts THOR security scanner logs into Timesketch-compatible format."
        )
        parser.add_argument("input_file", help="Path to THOR JSON file")
        parser.add_argument(
            "-o",
            dest="output_file",
            help="Output file path (default:<input_file>_mapped.jsonl)",
            default=None
        )
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        args = parser.parse_args()

        if args.verbose:
            LoggerConfig.setup_root_logger(level=logging.DEBUG)
        else:
            LoggerConfig.setup_root_logger(level=logging.INFO)

        if not args.output_file:
            input_file_name = os.path.splitext(args.input_file)[0]
            args.output_file = f"{input_file_name}_mapped.jsonl"

        output_dir = os.path.dirname(args.output_file)
        if output_dir and not os.path.isdir(output_dir):
            logger.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)

        return {
            "input_file": args.input_file,
            "output_file": args.output_file,
            "verbose": args.verbose
        }

    @staticmethod
    def run():
        args = MainControllerCLI.parse_arguments()
        input_file = args["input_file"]
        output_file = args["output_file"]

        success, thor_logs = THORJSONInputReader.get_valid_json(input_file)
        if not success:
            logger.error("Failed to open or read input file.")
            exit(1)

        flattener = JSONFlattener()
        output_writer = THORJSONOutputWriter(output_file)
        try:
            for json_line in thor_logs:

                flattened_json = flattener.flatten_jsonl(json_line)
                mapper = THORJSONLogVersionMapper.get_mapper(flattened_json)
                mapped_events = mapper.map_thor_events(flattened_json)

                if mapped_events:
                    output_writer.write_mapped_logs(mapped_events)

            logger.info(f"THOR-TS-Mapper completed successfully.")

        except Exception as e:
            logger.error(f"Error processing THOR logs: {e}")
            exit(1)
        finally:
            output_writer.close()


if __name__ == "__main__":
    # MainControllerCLI.run()

    input_file = "../thor10march.json"
    output_file = "../thor10march_mapped.jsonl"
    success, thor_logs = THORJSONInputReader.get_valid_json(input_file)
    if not success:
        logger.error("Failed to open or read input file.")
        exit(1)
    flattener = JSONFlattener()


    output_file = THORJSONOutputWriter(output_file).open()
    try:
        for json_line in thor_logs:

            flattened_json = flattener.flatten_jsonl(json_line)
            mapper = THORJSONLogVersionMapper.get_mapper(flattened_json)
            mapped_events = mapper.map_thor_events(flattened_json)
            if mapped_events:
                output_file.write_mapped_logs(mapped_events)

        logger.info(f"THOR-TS-Mapper completed successfully.")
    except Exception as e:
        logger.error(f"Error processing THOR logs: {e}")
        exit(1)
    finally:
        output_file.close()