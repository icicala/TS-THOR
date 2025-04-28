# language: python
import logging
from rich.console import Console
from rich.logging import RichHandler

class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if record.levelno == logging.DEBUG:
            level_color = "[dim cyan]"
        elif record.levelno == logging.INFO:
            level_color = "[green]"
        elif record.levelno == logging.WARNING:
            level_color = "[yellow]"
        elif record.levelno == logging.ERROR:
            level_color = "[red]"
        else:
            level_color = ""
        formatted_msg = super().format(record)
        return f"{level_color}{record.levelname}[/] {formatted_msg}"

class LoggerConfig:
    console = Console()

    @classmethod
    def setup_root_logger(cls, level: int = logging.INFO) -> None:
        handler = RichHandler(
            console=cls.console,
            rich_tracebacks=True,
            show_path=False,
            markup=True,
            log_time_format="[%Y-%m-%d %H:%M:%S]",
            show_level=False,
            enable_link_path=False
        )
        formatter = ColorFormatter("%(message)s")
        handler.setFormatter(formatter)
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[handler]
        )

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)