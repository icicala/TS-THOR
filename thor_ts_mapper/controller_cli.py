# python
import argparse
import os
import logging
from typing import Dict, List
from thor_ts_mapper.thor_input_reader import THORJSONInputReader
from thor_ts_mapper.thor_output_writer import THORJSONOutputWriter
from thor_ts_mapper.thor_timesketch_mapper import ThorTimesketchMapper
from thor_ts_mapper.event_category import EventCategory
from thor_ts_mapper.logger_config import LoggerConfig


logger = LoggerConfig.get_logger(__name__)



class MainControllerCLI:
    @staticmethod
    def parse_arguments() -> Dict[str, str]:
        default_folder = os.path.join(os.getcwd(), "timesketch_thor_logs")
        parser = argparse.ArgumentParser(
            description="THOR-TS-Mapper is a high-performance tool that converts THOR security scanner logs into Timesketch-compatible timeline format."
        )
        parser.add_argument("input_file", help="Path to THOR JSON file")
        parser.add_argument(
            "-o",
            dest="output_folder",
            help="Output folder path",
            default=default_folder
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

        if not os.path.isdir(args.output_folder):
            logger.info(f"Creating output directory: {args.output_folder}")
            os.makedirs(args.output_folder, exist_ok=True)

        return {"input_file": args.input_file,
                "output_folder": args.output_folder,
                "verbose": args.verbose}

    @staticmethod
    def generate_output_files(output_folder: str) -> Dict[str, str]:
        output_file = {}
        for category in EventCategory:
            filename = EventCategory.get_output_filename(category)
            output_file[category.value] = os.path.join(output_folder, filename)
        return output_file

    @staticmethod
    def read_logs(input_file: str) -> List[Dict]:
        success, logs = THORJSONInputReader.read_file(input_file)
        if not success or not logs:
            logger.error("Failed to read input file or no valid logs found.")
            exit(1)
        return logs

    @staticmethod
    def map_logs(logs: List[Dict]) -> Dict[str, List[Dict]]:
        categorized_events = {category.value: [] for category in EventCategory}

        for log in logs:
            mapped = ThorTimesketchMapper.map_and_categorize(log)
            for category, events in mapped.items():
                if category in categorized_events:
                    categorized_events[category].extend(events)
        return categorized_events

    @staticmethod
    def write_outputs(categorized_events: Dict[str, List[Dict]], output_files: Dict[str, str]) -> bool:
        overall_success = True
        for category, events in categorized_events.items():
            if events:
                logger.info(f"Writing {len(events)} {category} events to {output_files[category]}")
                if not THORJSONOutputWriter.write_timesketch_data(events, output_files[category]):
                    logger.error(f"Failed to write {category} events")
                    overall_success = False
            else:
                logger.info(f"No {category} events to write.")
        return overall_success

    @staticmethod
    def run():
        args = MainControllerCLI.parse_arguments()
        input_file = args["input_file"]
        output_folder = args["output_folder"]

        output_files = MainControllerCLI.generate_output_files(output_folder)
        THOR_logs = MainControllerCLI.read_logs(input_file)

        categorized_events = MainControllerCLI.map_logs(THOR_logs)
        overall_success = MainControllerCLI.write_outputs(categorized_events, output_files)

        if overall_success:
            logger.info("THOR-TS-Mapper completed successfully.")
            exit(0)
        else:
            logger.error("THOR-TS-Mapper encountered errors during procesing.")
            exit(1)


if __name__ == "__main__":
    MainControllerCLI.run()
