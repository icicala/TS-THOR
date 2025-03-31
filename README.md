# THOR-TS-Mapper

Converts THOR APT scanner logs to Timesketch-compatible timeline format.

## How It Works

1. Validates and reads the input THOR JSON file
2. Extracts timestamps from JSON entries
3. Categorizes events based on module and timestamps
4. Formats the timestamps for Timesketch compatibility
5. Writes the categorized events to separate output files

## Installation
```bash
git clone https://github.com
cd thor-ts-mapper
pip install .
```
## Usage
```bash
thor-ts-mapper /path/to/thor_logs.jsonl -o /path/to/output/folder -v
```
## Output Files

The tool generates three different output files in the specified output folder:

* `THOR_metadata.jsonl`: Contains scan metadata events
* `THOR_single_timestamp.jsonl`: Contains events with a single timestamp
* `THOR_multi_timestamp.jsonl`: Contains events with multiple timestamps