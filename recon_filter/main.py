"""
Main Typer application entrypoint with bilingual interactive menu and CLI routing.
"""
import sys
import typer
import questionary
from rich.console import Console

from recon_filter.version import __version__
from recon_filter.engine.update_check import UpdateChecker
from recon_filter.i18n import t, set_language

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
        f"Recon-Filter v{__version__} — Risk Intelligence Filtering Engine.\n\n"
        "Stream-processing CLI for extracting URLs, credentials, and high-risk\n"
        "targets from massive datasets with risk scoring and endpoint heuristics.\n\n"
        "Features: --intelligent risk scoring, --smart-mode fuzzy matching,\n"
        "multi-format preservation (TXT/JSON/CSV/PDF), URL clustering,\n"
        "parameter extraction, and bilingual interface (EN/ID).\n\n"
        "Update: yay -Syu recon-filter (Arch) | pip install --upgrade recon-filter"
    ),
    add_completion=False,
    invoke_without_command=True,
    no_args_is_help=False,
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


def _select_language():
    """Prompt for language selection."""
    lang = questionary.select(
        "Select Language / Pilih Bahasa:",
        choices=["English", "Bahasa Indonesia"],
    ).ask()

    if lang == "Bahasa Indonesia":
        set_language("id")
    else:
        set_language("en")


def run_interactive_menu():
    """Bilingual interactive menu for recon-filter."""
    console.print(f"\n[bold cyan]Recon Filter v{__version__}[/bold cyan]\n")

    _select_language()

    choice = questionary.select(
        t("menu_select"),
        choices=[
            t("menu_filter"),
            t("menu_intelligent"),
            t("menu_url"),
            t("menu_settings"),
            t("menu_help"),
            t("menu_exit"),
        ],
    ).ask()

    import os

    if choice == t("menu_filter"):
        os.system("recon-filter filter")
    elif choice == t("menu_intelligent"):
        console.print(f"[yellow]{t('hint_intelligent')}[/yellow]")
        os.system("recon-filter filter --intelligent")
    elif choice == t("menu_url"):
        console.print(f"[yellow]{t('hint_url')}[/yellow]")
        os.system("recon-filter filter --extract-params")
    elif choice == t("menu_settings"):
        os.system("recon-filter config")
    elif choice == t("menu_help"):
        os.system("recon-filter --help")
    else:
        raise typer.Exit(0)


@app.callback()
def global_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
    no_menu: bool = typer.Option(False, "--no-menu", help="Bypass interactive menu for direct CLI usage."),
    no_update_check: bool = typer.Option(False, "--no-update-check", help="Disable update checking."),
    force_update_check: bool = typer.Option(False, "--force-update-check", help="Force a remote update check."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """
    Recon-Filter v2 — Risk Intelligence Filtering Engine.

    Supports: Arch Linux, Debian, Ubuntu, Fedora, CachyOS, Manjaro, openSUSE.
    Update: yay -Syu recon-filter | pipx upgrade recon-filter
    """
    if version:
        console.print(f"recon-filter version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()

    if force_update_check:
        checker = UpdateChecker()
        checker.check_for_updates(force=True)

    if ctx.invoked_subcommand is None and not no_menu and not version:
        run_interactive_menu()


if __name__ == "__main__":
    app()
