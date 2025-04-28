import logging
from rich.console import Console
from rich.logging import RichHandler

class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if record.levelno == logging.INFO:
            message = f"[green]{message}[/green]"
        elif record.levelno == logging.WARNING:
            message = f"[yellow]{message}[/yellow]"
        elif record.levelno == logging.ERROR:
            message = f"[red]{message}[/red]"
        return message

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
            show_level=True,
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