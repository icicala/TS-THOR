from typing import Iterator, Dict, Any
from thor2timesketch.input.json_reader import JsonReader


class ReaderProcessor:
    def __init__(self) -> None:
        self.input_reader = JsonReader()

    def read(self, input_file: str) -> Iterator[Dict[str, Any]]:
        return self.input_reader.get_valid_data(input_file)