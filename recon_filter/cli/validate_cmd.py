"""
Validate subcommand safely testing regex payloads and keyword dictionaries before live executions.
"""
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from recon_filter.filters import compile_regex
from recon_filter.utils import setup_logger

app = typer.Typer()
console = Console()

@app.command("validate", help="Strictly validate Regex patterns or keyword files before executing pipelines.")
def validate_cmd(
    regex: Optional[str] = typer.Option(None, "--regex", "-r", help="Regex to test compilation."),
    keyword_file: Optional[Path] = typer.Option(None, "--keyword-file", "-k", help="Keyword file to sanity check."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    logger = setup_logger(verbose)
    
    success = True
    
    if regex:
        try:
            compile_regex(regex, False) # test parse without executing against log line
            console.print(f"✅ [bold green]Regex Pattern Validation Successful:[/bold green] {regex}")
        except ValueError as e:
            console.print(f"❌ [bold red]Regex Pattern Failed Validation:[/bold red] {e}")
            success = False
            
    if keyword_file:
        if not keyword_file.exists():
            console.print(f"❌ [bold red]Keyword file not found:[/bold red] {keyword_file}")
            success = False
        else:
            try:
                with keyword_file.open('r') as f:
                    words = [line.strip() for line in f if line.strip()]
                    
                if not words:
                    console.print(f"⚠️ [bold yellow]Keyword list parsed but empty.[/bold yellow] Target: {keyword_file}")
                else:
                    console.print(f"✅ [bold green]Keyword Dictionary Parsed Successfully.[/bold green] Targets: {len(words)} lines.")
            except Exception as e:
                console.print(f"❌ [bold red]Failed to decode keyword manifest:[/bold red] {e}")
                success = False
                
    if not regex and not keyword_file:
        logger.warning("Empty validation sequence. Feed arguments via --regex or --keyword-file.")
        
    if not success:
        raise typer.Exit(code=1)
