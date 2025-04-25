import logging
from rich.console import Console
from rich.logging import RichHandler
from typing import Optional

class LoggerConfig:

    console = Console()

    @classmethod
    def setup_root_logger(cls, level: int = logging.INFO) -> None:
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=cls.console, rich_tracebacks=True)]
        )

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)