"""
Version subcommand.
"""
import typer
from rich.console import Console
from recon_filter import __version__

app = typer.Typer()

@app.command("version", help="Print the current version of recon-filter.")
def version_cmd():
    console = Console()
    console.print(f"recon-filter version [bold cyan]{__version__}[/bold cyan]")
