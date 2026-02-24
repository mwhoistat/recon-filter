"""
Update instructional sequence providing deterministic pip routines locally.
"""
import typer
from rich.console import Console
from recon_filter.version import __version__
from recon_filter.engine.update_check import UpdateChecker

app = typer.Typer()
console = Console()

@app.command("update", help="Displays non-destructive instructions on upgrading recon-filter locally.")
def update_cmd(
    check: bool = typer.Option(False, "--check", "-c", help="Force ping remote remote repository strictly crossing the 24-hr cache boundary.")
):
    console.print(f"\n[cyan]recon-filter Current Local Version:[/cyan] [bold]v{__version__}[/bold]")
    
    if check:
        console.print("[cyan]Connecting to upstream releases...[/cyan]")
        checker = UpdateChecker()
        checker.check_for_updates(force=True)
    
    console.print("\n[bold]Upgrade Instructions:[/bold]")
    console.print("Recon-Filter manages upgrades structurally spanning standard python native distributions.")
    console.print("\n[green]If installed via pip (Recommended):[/green]")
    console.print("  [bold]pip install --upgrade recon-filter[/bold]")
    
    console.print("\n[green]If running from a cloned source directory:[/green]")
    console.print("  [bold]git pull origin main[/bold]")
    console.print("  [bold]pip install .[/bold]\n")
