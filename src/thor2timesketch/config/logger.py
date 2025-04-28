import logging
from rich.console import Console
from rich.logging import RichHandler

class LoggerConfig:
    console = Console()

    @classmethod
    def setup_root_logger(cls, level: int = logging.INFO) -> None:
        handler = RichHandler(
            console=cls.console,
            rich_tracebacks=True,
            show_path=False,
            markup=True,
            show_time=True,
            show_level=True,
            enable_link_path=False
        )

        logging.basicConfig(
            level=level,
            format="%(message)s",
            handlers=[handler]
        )

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)