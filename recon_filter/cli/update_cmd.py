"""
Update instructional sequence providing deterministic upgrade routines
with distro-specific package manager detection.
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from recon_filter.version import __version__
from recon_filter.engine.update_check import UpdateChecker

app = typer.Typer()
console = Console()


def _detect_distro() -> str:
    """Detect the current Linux distribution from /etc/os-release."""
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return "unknown"
    try:
        text = os_release.read_text()
        for line in text.splitlines():
            if line.startswith("ID="):
                return line.split("=", 1)[1].strip().strip('"').lower()
    except Exception:
        pass
    return "unknown"


_DISTRO_INSTRUCTIONS = {
    "arch": [
        ("yay (AUR)", "yay -Syu recon-filter"),
        ("pacman (local PKGBUILD)", "cd ~/Tools/recon-filter && makepkg -si"),
        ("pipx", "pipx upgrade recon-filter"),
    ],
    "manjaro": [
        ("yay (AUR)", "yay -Syu recon-filter"),
        ("pipx", "pipx upgrade recon-filter"),
    ],
    "cachyos": [
        ("yay (AUR)", "yay -Syu recon-filter"),
        ("pacman (local PKGBUILD)", "cd ~/Tools/recon-filter && makepkg -si"),
        ("pipx", "pipx upgrade recon-filter"),
    ],
    "debian": [
        ("pip", "pip install --upgrade recon-filter"),
        ("pipx", "pipx upgrade recon-filter"),
    ],
    "ubuntu": [
        ("pip", "pip install --upgrade recon-filter"),
        ("pipx", "pipx upgrade recon-filter"),
    ],
    "fedora": [
        ("pip", "pip install --upgrade recon-filter"),
        ("pipx", "pipx upgrade recon-filter"),
    ],
    "opensuse-tumbleweed": [
        ("pip", "pip install --upgrade recon-filter"),
        ("pipx", "pipx upgrade recon-filter"),
    ],
}


@app.command("update", help="Displays non-destructive instructions on upgrading recon-filter locally.")
def update_cmd(
    check: bool = typer.Option(False, "--check", "-c", help="Force ping the remote repository crossing the 24-hr cache boundary."),
):
    console.print(f"\n[cyan]recon-filter Current Local Version:[/cyan] [bold]v{__version__}[/bold]")

    if check:
        console.print("[cyan]Connecting to upstream releases...[/cyan]")
        checker = UpdateChecker()
        checker.check_for_updates(force=True)

    distro = _detect_distro()
    console.print(f"[cyan]Detected Distribution:[/cyan] [bold]{distro}[/bold]\n")

    instructions = _DISTRO_INSTRUCTIONS.get(distro, _DISTRO_INSTRUCTIONS.get("debian"))

    table = Table(title="Upgrade Instructions")
    table.add_column("Method", style="green")
    table.add_column("Command", style="bold white")

    for method, cmd in instructions:
        table.add_row(method, cmd)

    # Always show the git-based option
    table.add_row("Git Source", "git pull origin main && pip install .")

    console.print(table)
    console.print()
