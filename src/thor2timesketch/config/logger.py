
import logging
from rich.console import Console
from rich.logging import RichHandler

class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        time_str = self.formatTime(record, self.datefmt)
        time_str = f"[white]{time_str}[/white]"

        if record.levelno == logging.DEBUG:
            level_color = "[blue]"
        elif record.levelno == logging.INFO:
            level_color = "[green]"
        elif record.levelno == logging.WARNING:
            level_color = "[yellow]"
        elif record.levelno == logging.ERROR:
            level_color = "[red]"
        else:
            level_color = "[white]"
        level_str = f"{level_color}{record.levelname}[/]"
        message_str = f"[white]{record.getMessage()}[/white]"
        return f"{time_str} {level_str} {message_str}"


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
        formatter = ColorFormatter("%(asctime)s %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]")
        handler.setFormatter(formatter)
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(message)s",
            datefmt="[%H:%M:%S]",
            handlers=[handler]
        )

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)