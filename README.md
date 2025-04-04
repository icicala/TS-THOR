# THOR to Timesketch Mapper
This log conversion utility makes it easy to import THOR logs into Timesketch. Combining THOR findings on a shared timeline it enables cybersecurity analysts to enhance detection and analysis of malicious activity.
## Description
This utility processes THOR JSON logs and maps them to Timesketch’s required timeline format by:

* Extracting relevant fields from THOR logs

* Generating entries with the required Timesketch fields: message, datetime, and timestamp_desc

* Handling thor events with multiple timestamps by duplicating the log entry for each timestamp found
## Field Mapping Logic
This utility maps the following fields from THOR logs to Timesketch's required format:

* **message**: A key detection detail generated by THOR, providing context or justification for the event.

* **datetime**:
  * The THOR scan execution time, or
  * A timestamp found within the specific event related to a module or feature.

* **timestamp_desc**:
  * If datetime refers to the THOR scan start time → "Timestamp of THOR scan execution"
  * If datetime originates from a specific module field → "ModuleName - FieldName" (e.g., FileScan - modified)

**Note**: **ruledate** are not mapped to datetime.

This utility supports THOR JSON log format v2 and is designed with forward compatibility for JSON log format v3.
## HOW the utility works

1. Validates and reads the input THOR JSON file
2. Flattening THOR logs for efficient indexing and searching
3. Identifies the THOR log version and selects the appropriate mapper
4. Extracts relevant information and timestamps from each log entry
5. Maps THOR fields to Timesketch's required format (message, datetime, timestamp_desc)
6. Writes the mapped events to a single JSONL output file
7. The resulting .jsonl file can be ingested into Timesketch using either the Web UI or the [Importer CLI tool](https://timesketch.org/guides/user/cli-client/)
## Requirements
* Python 3.9 or higher
* THOR JSON logs (v2 or v3)
## Installation
```bash
git clone https://github.com/[TBD]/thor-ts-mapper
cd thor_ts_mapper
pip install .
```
## Usage
```bash
thor_ts_mapper /path/to/thor_logs.json -o /path/to/output/filename -v
```
### Arguments
* **input_file** - Path to THOR JSON file (required)
* **-o output_file** - Output file path (optional, default: <input_file_name>_mapped.jsonl)
* **-v, --verbose** - Enable verbose output (optional)
## Output Files
The tool converts THOR JSON logs to Timesketch-compatible format. If no output file is specified, the output will be written to the same location as the input file with **"<input_file_name>_mapped.jsonl"** appended.