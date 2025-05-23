from datetime import datetime
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich import box

class ConsoleConfig:
    LEVELS = {
        "DEBUG": 1,
        "INFO": 2,
        "SUCCESS": 3,
        "WARNING": 5,
        "ERROR": 8,
    }
    min_level = LEVELS["INFO"]


    theme = Theme({
        "timestamp": "grey50",
        "level.INFO": "green",
        "level.DEBUG": "magenta",
        "level.WARNING": "yellow",
        "level.ERROR": "bold red",
        "level.SUCCESS": "bold green",
    })
    console = Console(theme=theme, markup=True, highlight=False)

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%d %b %Y %H:%M:%S")

    @classmethod
    def _print(cls, level: str, message: str) -> None:
        if cls.LEVELS[level] < cls.min_level:
            return
        ts = cls._timestamp()
        cls.console.print(
            f"[timestamp]{ts}[/timestamp] "
            f"[level.{level}]{level}[/level.{level}] {message}"
        )

    @classmethod
    def info(cls, message: str) -> None:
        cls._print("INFO", message)

    @classmethod
    def debug(cls, message: str) -> None:
        cls._print("DEBUG", message)

    @classmethod
    def warning(cls, message: str) -> None:
        cls._print("WARNING", message)

    @classmethod
    def error(cls, message: str) -> None:
        cls._print("ERROR", message)

    @classmethod
    def success(cls, message: str) -> None:
        cls._print("SUCCESS", message)


    @classmethod
    def panel(cls, msg: str, title: str = "thor2ts", style: str = "cyan") -> None:
        cls.console.print(
            Panel.fit(msg, title=title, style=style, box=box.ROUNDED)
        )

    @classmethod
    def set_verbose(cls, verbose: bool) -> None:
        cls.min_level = cls.LEVELS["DEBUG"] if verbose else cls.LEVELS["INFO"]