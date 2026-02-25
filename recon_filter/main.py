"""
Main Typer application entrypoint handling top-level routing and interactive menus.
"""
import sys
import typer
import questionary
from rich.console import Console

from recon_filter.version import __version__
from recon_filter.engine.update_check import UpdateChecker

from recon_filter.cli.filter_cmd import filter_cmd
from recon_filter.cli.stats_cmd import stats_cmd
from recon_filter.cli.validate_cmd import validate_cmd
from recon_filter.cli.version_cmd import version_cmd
from recon_filter.cli.doctor_cmd import doctor_cmd
from recon_filter.cli.clean_cmd import clean_cmd
from recon_filter.cli.config_cmd import init_cmd as config_cmd
from recon_filter.cli.benchmark_cmd import benchmark_cmd
from recon_filter.cli.update_cmd import update_cmd
from recon_filter.cli.selftest_cmd import selftest_cmd

app = typer.Typer(
    name="recon-filter",
    help=(
        "Recon-Filter v1.0.0 High-Performance File Filtering Engine.\n\n"
        "A strict, streaming memory-safe CLI designed for extracting URLs, "
        "passwords, and critical tokens from massive multi-gigabyte datasets "
        "across Arch, Debian, Ubuntu, and Fedora Linux nodes perfectly."
    ),
    add_completion=False,
    invoke_without_command=True, # Critical for interactive menu routing
    no_args_is_help=False
)

app.command(name="filter")(filter_cmd)
app.command(name="stats")(stats_cmd)
app.command(name="validate")(validate_cmd)
app.command(name="version")(version_cmd)
app.command(name="doctor")(doctor_cmd)
app.command(name="clean")(clean_cmd)
app.command(name="config")(config_cmd)
app.command(name="benchmark")(benchmark_cmd)
app.command(name="update")(update_cmd)
app.command(name="self-test")(selftest_cmd)

console = Console()

def run_interactive_menu():
    """Builds a clean, professional, non-emoji interactive interface for recon-filter."""
    console.print(f"\n[bold cyan]Recon Filter v{__version__}[/bold cyan]\n")
    
    choice = questionary.select(
        "Select an option:",
        choices=[
            "Filter file",
            "Analyze URLs",
            "Generate statistics",
            "Configuration",
            "Help",
            "Exit"
        ]
    ).ask()
    
    if choice == "Filter file":
        import os
        os.system("recon-filter filter")
    elif choice == "Analyze URLs":
        console.print("[yellow]Hint:[/yellow] URL Analysis uses the filter engine natively.")
        import os
        os.system("recon-filter filter --extract-params")
    elif choice == "Generate statistics":
        import os
        os.system("recon-filter stats --help")
    elif choice == "Configuration":
        import os
        os.system("recon-filter config")
    elif choice == "Help":
        import os
        os.system("recon-filter --help")
    else:
        # Exit implicitly securely
        raise typer.Exit(0)

@app.callback()
def global_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
    no_menu: bool = typer.Option(False, "--no-menu", help="Bypass interactive menu when no args provided."),
    no_update_check: bool = typer.Option(False, "--no-update-check", help="Disable checking GitHub for updates."),
    force_update_check: bool = typer.Option(False, "--force-update-check", help="Force a check for updates, overriding cache."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output.")
):
    """
    Recon-Filter High-Performance Text Extraction Engine.
    
    Compatible Targets: Arch Linux, Debian, Ubuntu, Fedora.
    """
    if version:
        console.print(f"recon-filter version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()
        
    # Asynchronous lightweight update checks natively binding globally
    if not no_update_check:
        checker = UpdateChecker()
        checker.check_for_updates(force=force_update_check)

    # Boot into interactive menu if zero targets supplied natively
    if ctx.invoked_subcommand is None and not no_menu and not version:
        run_interactive_menu()

if __name__ == "__main__":
    app()
