from pathlib import Path
from typing import Sequence
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.constants import EMPTY_FILE
from thor2timesketch.exceptions import (
    FileNotFoundError,
    FileNotReadableError,
    EmptyFileError,
    InvalidFileExtensionError
)

logger = LoggerConfig.get_logger(__name__)


class FileValidator:
    def __init__(self, valid_extensions: Sequence[str]) -> None:
        self.valid_extensions = {ext.lower() for ext in valid_extensions}

    def validate_file(self, file_path: Path) -> Path:
        self._check_file_exists(file_path)
        self._check_file_readable(file_path)
        self._check_file_not_empty(file_path)
        self._check_file_extension(file_path)
        logger.info(f"File '{file_path}' is valid and ready for processing.")
        return file_path

    def _check_file_exists(self, file_path: Path) -> None:
        if not file_path.is_file():
            error_msg = f"File '{file_path}' does not exist."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        logger.debug(f"File '{file_path}' is valid.")

    def _check_file_readable(self, file_path: Path) -> None:
        try:
            with file_path.open("rb"):
                pass
        except OSError as e:
            error_msg = f"File '{file_path}' is not readable: {e}"
            logger.error(error_msg)
            raise FileNotReadableError(error_msg) from None

    def _check_file_not_empty(self, file_path: Path) -> None:
        if file_path.stat().st_size == EMPTY_FILE:
            error_msg = f"File '{file_path}' is empty."
            logger.error(error_msg)
            raise EmptyFileError(error_msg)
        logger.debug(f"File '{file_path}' is not empty.")

    def _check_file_extension(self, file_path: Path) -> None:
        ext = file_path.suffix.lower()
        if ext not in self.valid_extensions:
            expected = ", ".join(self.valid_extensions)
            error_msg = (
                f"Invalid file extension for '{file_path}'. "
                f"Expected one of: ['{expected}'], but got: '{ext!r}'"
            )
            logger.error(error_msg)
            raise InvalidFileExtensionError(error_msg)
        logger.debug(f"File '{file_path}' has a valid extension: '{ext}'")
