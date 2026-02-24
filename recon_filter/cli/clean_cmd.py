"""
Clean subcommand purging logs, structural caches, and backup artifacts safely.
"""
import shutil
from pathlib import Path

import typer
import questionary

from recon_filter.utils import setup_logger
from recon_filter.engine.cache import CacheManager

app = typer.Typer()

@app.command("clean", help="Purges all `.bak` backups, `.recon_cache` states, and `.log` auditing traces originating from executions.")
def clean_cmd(
    target_dir: str = typer.Option("./", "--target", "-t", help="Directory root to purge from."),
    force: bool = typer.Option(False, "--force", "-f", help="Bypass strict confirmation barriers."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose tracing."),
):
    logger = setup_logger(verbose)
    root = Path(target_dir).resolve()
    
    if not force:
        confirm = questionary.confirm(
            f"WARNING: This will recursively delete all `.bak` backups, `/logs` directories, and `.recon_cache` signatures inside {root}. Proceed?"
        ).ask()
        
        if not confirm:
            logger.info("Purge operation cancelled by secure user abort.")
            raise typer.Exit(0)
            
    # Purge Audit Logs
    logs_dir = root / "logs"
    if logs_dir.exists() and logs_dir.is_dir():
        shutil.rmtree(logs_dir)
        logger.info(f"Audit log directory pruned successfully: {logs_dir}")
        
    # Purge Cache Directory natively mapping CacheManager defaults
    cacher = CacheManager()
    if cacher.cache_dir.exists():
        cacher.purge()
        logger.info(f"SHA-256 Engine Cache bindings purged safely.")
        
    # Purge Backups Recursively
    count = 0
    for bak_file in root.rglob("*.bak"):
        try:
            bak_file.unlink()
            count += 1
        except Exception as e:
            logger.warning(f"Failed pruning cached backup artifact {bak_file}: {e}")
            
    logger.info(f"Purge sequence complete. Deleted {count} total structural backups natively.")
