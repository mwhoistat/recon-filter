"""
Initialization module establishing strict YAML configuration profiles natively.
"""
from pathlib import Path
import typer
from recon_filter.config import ConfigManager
from recon_filter.utils import setup_logger

app = typer.Typer()

@app.command("init", help="Generates standard `.yaml` configurations mapping professional profiles locally.")
def init_cmd(
    filepath: Path = typer.Option(Path("recon-filter.yaml"), "--file", "-f", help="Output state map artifact location."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose tracing."),
):
    logger = setup_logger(verbose)
    
    try:
        ConfigManager.generate_default(filepath)
        logger.info(f"Default professional configuration state fully persisted locally globally to {filepath}.")
    except Exception as e:
        logger.error(f"Failed configuration generation protocol natively: {e}")
        raise typer.Exit(1)
