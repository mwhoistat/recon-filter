"""
Main Typer application entrypoint handling top-level routing and interactive menus.
"""
import sys
import typer
import questionary
from rich.console import Console

from recon_filter.version import __version__
from recon_filter.engine.update_check import UpdateChecker

from recon_filter.cli.filter_cmd import app as filter_app
from recon_filter.cli.stats_cmd import app as stats_app
from recon_filter.cli.validate_cmd import app as validate_app
from recon_filter.cli.version_cmd import app as version_app
from recon_filter.cli.doctor_cmd import app as doctor_app
from recon_filter.cli.clean_cmd import app as clean_app
from recon_filter.cli.config_cmd import app as config_app
from recon_filter.cli.benchmark_cmd import app as benchmark_app
from recon_filter.cli.update_cmd import app as update_app
from recon_filter.cli.selftest_cmd import app as selftest_app

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

app.add_typer(filter_app, name="filter")
app.add_typer(stats_app, name="stats")
app.add_typer(validate_app, name="validate")
app.add_typer(version_app, name="version")
app.add_typer(doctor_app, name="doctor")
app.add_typer(clean_app, name="clean")
app.add_typer(config_app, name="config")
app.add_typer(benchmark_app, name="benchmark")
app.add_typer(update_app, name="update")
app.add_typer(selftest_app, name="self-test")

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
