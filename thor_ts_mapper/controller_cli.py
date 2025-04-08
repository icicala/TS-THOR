import os
import sys

import click

from thor_ts_mapper.logger_config import LoggerConfig
# from thor_ts_mapper.thor_output_to_file import THORConverterToFile
from thor_ts_mapper.thor_output_to_ts import THORIngestToTS

logger = LoggerConfig.get_logger(__name__)


class MainControllerCLI:
    @click.group(context_settings={"help_option_names": ["-h", "--help"]})
    @click.version_option(version=__import__('thor_ts_mapper').__version__, prog_name="thor2ts")
    def cli():
        """THOR to Timesketch Mapper.

        This tool converts THOR security scanner logs to Timesketch-compatible format.
        """
        pass


    @cli.command()
    @click.argument('input_file', type=click.Path(exists=True))
    @click.option('-o', '--output-file', type=click.Path(), help="Output file path (default:<input_file>_mapped.jsonl)")
    @click.option('-v', '--verbose', is_flag=True, help="Enable verbose output")
    def convert(input_file, output_file, verbose):
        """Convert THOR logs to Timesketch format."""
        if verbose:
            LoggerConfig.setup_root_logger(level="DEBUG")
        else:
            LoggerConfig.setup_root_logger(level="INFO")

        if not output_file:
            input_file_name = os.path.splitext(input_file)[0]
            output_file = f"{input_file_name}_mapped.jsonl"
        elif not output_file.lower().endswith('.jsonl'):
            original = output_file
            output_file = f"{os.path.splitext(output_file)[0]}.jsonl"
            logger.info(f"Changed output file from '{original}' to '{output_file}' to ensure JSONL format")

        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.isdir(output_dir):
            logger.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)

        # processor = THORConverterToFile() redo it
        success, events_count = processor.converter_to_file(input_file, output_file)

        if success:
            logger.info(f"Successfully mapped {events_count} events to {output_file}")
            logger.info(
                "Nextron's mission continues -> we detect hackers <-. Launch Timesketch and ingest THOR logs via Web UI or CLI and let the hunt begin.")
        else:
            sys.exit(1)


    @cli.command()
    @click.argument('input_file', type=click.Path(exists=True))
    @click.option('-o', '--output-file', type=click.Path(),
                  help="Temporary output file path (default:<input_file>_mapped.jsonl)")
    @click.option('--sketch', type=int, help="Sketch ID to ingest into")
    @click.option('-v', '--verbose', is_flag=True, help="Enable verbose output")
    @click.option('--timeline-name', help="Name for the timeline in Timesketch (default: input filename)")
    def ingest(input_file, output_file, sketch, verbose, timeline_name):
        """Convert THOR logs and ingest them into Timesketch."""
        if verbose:
            LoggerConfig.setup_root_logger(level="DEBUG")
        else:
            LoggerConfig.setup_root_logger(level="INFO")

        # Set default output file if not specified
        if not output_file:
            input_file_name = os.path.splitext(input_file)[0]
            output_file = f"{input_file_name}_mapped.jsonl"
        elif not output_file.lower().endswith('.jsonl'):
            original = output_file
            output_file = f"{os.path.splitext(output_file)[0]}.jsonl"
            logger.info(f"Changed output file from '{original}' to '{output_file}' to ensure JSONL format")

        # Set default timeline name if not specified
        if not timeline_name:
            timeline_name = os.path.basename(input_file)

        # Process the THOR logs first
        processor = THORConverterToFile()
        success, events_count = processor.converter_to_file(input_file, output_file)

        if not success:
            logger.error("Failed to process THOR logs, aborting ingestion")
            sys.exit(1)

        # Connect to Timesketch and ingest the file
        ts_client = THORIngestToTS()
        if not ts_client.connect():
            logger.error("Failed to connect to Timesketch")
            sys.exit(1)

        sketch_obj = ts_client.get_sketch(sketch)
        if not sketch_obj:
            logger.error("Failed to get sketch")
            sys.exit(1)

        success, ingested_count = ts_client.ingest_file(sketch_obj, output_file, timeline_name)
        if not success:
            logger.error("Failed to ingest file into Timesketch")
            sys.exit(1)

        logger.info(f"Successfully ingested {ingested_count} events into Timesketch sketch '{sketch_obj.name}'")


def main():
    cli()


if __name__ == "__main__":
    main()