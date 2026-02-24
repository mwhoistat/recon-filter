"""
Stats subcommand for parsing and formatting JSON statistics outputs beautifully.
"""
import json
from pathlib import Path

import typer
from rich.table import Table

from recon_filter.utils import setup_logger, console

app = typer.Typer()

@app.command("stats", help="Render exported statistics JSON to terminal UI.")
def stats_cmd(
    filepath: Path = typer.Argument(..., help="Path to exported JSON file."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose tracing."),
):
    logger = setup_logger(verbose)
    
    if not filepath.exists() or not filepath.is_file():
        logger.error(f"Cannot find statistics file at {filepath}")
        raise typer.Exit(1)
        
    try:
        with filepath.open('r') as f:
            data = json.load(f)
            
        table = Table(title=f"Recon Filter Stats Payload ([cyan]{filepath.name}[/cyan])", style="green")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        for key, val in data.items():
            formatted_key = key.replace("_", " ").title()
            table.add_row(formatted_key, str(val))
            
        console.print()
        console.print(table)
        
    except Exception as e:
        logger.error(f"Failed to parse statistics payload: {e}")
        raise typer.Exit(1)
