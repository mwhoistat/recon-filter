"""
Utility helper functions for recon-filter v3.
Ensures strict, professional tone mapping devoid of emojis or casual logs.
"""
import logging
from rich.console import Console

# Rich setup for terminal aesthetics (Strict, lean formats)
console = Console()

BANNER = r"""
  ██▀███   ▓█████  ▄████▄   ▒█████   ███▄    █  ▄▄▄██▀▀▀ ██▓ ██▓    ▄▄▄█████▓▓█████  ██▀███      
  ▓██ ▒ ██▒▓█   ▀ ▒██▀ ▀█  ▒██▒  ██▒ ██ ▀█   █    ▒██    ▓██▒▓██▒    ▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒   
  ▓██ ░▄█ ▒▒███   ▒▓█    ▄ ▒██░  ██▒▓██  ▀█ ██▒   ░██    ▒██▒▒██░    ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒   
  ▒██▀▀█▄  ▒▓█  ▄ ▒▓▓▄ ▄██▒▒██   ██░▓██▒  ▐▌██▒ ▓██▄██▓  ░██░▒██░    ░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄     
  ░██▓ ▒██▒░▒████▒▒ ▓███▀ ░░ ████▓▒░▒██░   ▓██░  ▓███▒   ░██░░██████▒  ▒██▒ ░ ░▒████▒░██▓ ▒██▒   
  ░ ▒▓ ░▒▓░░░ ▒░ ░░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒   ▒▓▒▒░   ░▓  ░ ▒░▓  ░  ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░   
    ░▒ ░ ▒░ ░ ░  ░  ░  ▒     ░ ▒ ▒░ ░ ░░   ░ ▒░   ▒ ░▒░    ▒ ░░ ░ ▒  ░    ░     ░ ░  ░  ░▒ ░ ▒░  
    ░░   ░    ░   ░        ░ ░ ░ ▒     ░   ░ ░    ░ ░ ░    ▒ ░  ░ ░     ░       ░     ░░   ░     
     ░        ░  ░░ ░          ░ ░           ░    ░   ░    ░      ░  ░          ░  ░   ░         
             ░                                                                                   
             Professional Stream Processing Engine for System Logs & Recon Data                  
"""

class RichHandler(logging.Handler):
    """Custom logging handler mapping logic via Rich explicitly avoiding tracebacks by default."""
    def emit(self, record):
        msg = self.format(record)
        if record.levelno >= logging.ERROR:
            console.print(f"[bold red]ERROR:[/bold red] {msg}")
        elif record.levelno >= logging.WARNING:
            console.print(f"[bold yellow]WARNING:[/bold yellow] {msg}")
        else:
            console.print(f"[cyan]INFO:[/cyan] {msg}")


def setup_logger(verbose: bool = False, quiet: bool = False) -> logging.Logger:
    """
    Configures the root logger for the application cleanly.
    """
    logger = logging.getLogger("recon_filter")
    
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if quiet:
        logger.addHandler(logging.NullHandler())
    else:
        # We explicitly print the banner here once natively.
        if not verbose and len(logging.getLogger().handlers) == 0:
             console.print(f"[bold blue]{BANNER}[/bold blue]")
             
        handler = RichHandler()
        formatter = logging.Formatter("%(message)s")
        if verbose:
            # Professional traceback mapping logic natively for engineers.
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
