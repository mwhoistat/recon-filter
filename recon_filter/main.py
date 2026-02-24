"""
Core production Typer entrypoint mounted via pyproject.toml metadata sequentially.
"""
import typer
from rich.console import Console

from recon_filter.version import __version__
from recon_filter.engine.update_check import UpdateChecker

from recon_filter.cli import (
    filter_cmd, 
    stats_cmd, 
    validate_cmd, 
    doctor_cmd,
    clean_cmd,
    config_cmd,
    benchmark_cmd,
    update_cmd,
    selftest_cmd
)

console = Console()
app = typer.Typer(
    help="Professional Stream Processing Engine for System Logs & Recon Data",
    add_completion=False,
    invoke_without_command=True, # Allows overriding standard `--version` mapping directly onto root context natively
)

app.add_typer(filter_cmd.app)
app.add_typer(stats_cmd.app)
app.add_typer(validate_cmd.app)
app.add_typer(doctor_cmd.app)
app.add_typer(clean_cmd.app)
app.add_typer(config_cmd.app)
app.add_typer(benchmark_cmd.app)
app.add_typer(update_cmd.app)
app.add_typer(selftest_cmd.app)

def render_banner():
    banner = f"""
  ██▀███   ▓█████  ▄████▄   ▒█████   ███▄    █  ▄▄▄██▀▀▀ ██▓ ██▓    ▄▄▄█████▓▓█████  ██▀███      
  ▓██ ▒ ██▒▓█   ▀ ▒██▀ ▀█  ▒██▒  ██▒ ██ ▀█   █    ▒██    ▓██▒▓██▒    ▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒   
  ▓██ ░▄█ ▒▒███   ▒▓█    ▄ ▒██░  ██▒▓██  ▀█ ██▒   ░██    ▒██▒▒██░    ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒   
  ▒██▀▀█▄  ▒▓█  ▄ ▒▓▓▄ ▄██▒▒██   ██░▓██▒  ▐▌██▒ ▓██▄██▓  ░██░▒██░    ░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄     
  ░██▓ ▒██▒░▒████▒▒ ▓███▀ ░░ ████▓▒░▒██░   ▓██░  ▓███▒   ░██░░██████▒  ▒██▒ ░ ░▒████▒░██▓ ▒██▒   
  ░ ▒▓ ░▒▓░░░ ▒░ ░░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒   ▒▓▒▒░   ░▓  ░ ▒░▓  ░  ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░   
             Professional Stream Processing Engine | [bold cyan]v{__version__}[/bold cyan]
    """
    console.print(banner)

def render_menu():
    menu = f"""
[bold cyan]Recon Filter v{__version__}[/bold cyan]
High-performance filtering and analysis tool

[bold]Available Commands:[/bold]
  [cyan]filter[/cyan]        Process and filter files
  [cyan]stats[/cyan]         Show statistics
  [cyan]validate[/cyan]      Validate input file
  [cyan]version[/cyan]       Show version information
  [cyan]self-test[/cyan]    Run internal diagnostics
  [cyan]benchmark[/cyan]    Run performance benchmarks
  [cyan]doctor[/cyan]       Run environment diagnostics
  [cyan]clean[/cyan]        Purge execution caches
  [cyan]config[/cyan]       Manage configurations
  [cyan]update[/cyan]       Show update instructions

Use:
  [bold]recon-filter <command> --help[/bold]
"""
    console.print(menu)

@app.callback()
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Print the explicit native engine version constraint."),
    no_update_check: bool = typer.Option(False, "--no-update-check", help="Disables the background GH version check payload securely."),
    verbose: bool = typer.Option(False, "--verbose", help="Renders massive decorative pipeline components.")
):
    """
    Global interceptor bound before any Subcommands trigger natively.
    """
    if version:
        console.print(f"recon-filter version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()
        
    if verbose:
        render_banner()
        
    # Check for underlying GitHub updates natively over 24-hr cache.
    # Exclude logic from standard diagnostic or update hooks inherently.
    if not no_update_check and ctx.invoked_subcommand not in ['update', 'version', 'clean', 'config'] and ctx.invoked_subcommand is not None:
        checker = UpdateChecker()
        checker.check_for_updates(quiet=False)
        
    if ctx.invoked_subcommand is None:
        if verbose:
             pass
        else:
            render_menu()
            
if __name__ == "__main__":
    app()
