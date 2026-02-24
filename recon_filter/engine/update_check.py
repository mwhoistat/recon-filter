"""
Background async update checker resolving GitHub traces natively.
Provides caching locking queries to a 24-hr delay preventing API spam.
"""
import json
import time
import urllib.request
import urllib.error

from recon_filter.version import __version__
from recon_filter.engine.cache import CacheManager
from rich.console import Console

console = Console()

class UpdateChecker:
    def __init__(self):
        self.cacher = CacheManager()
        self.state_file = self.cacher.cache_dir / "update_check.json"
        
        # 24 hours in seconds
        self.check_interval = 86400
        # Replace this URL natively with the actual raw version URL from GitHub upon deployment.
        self.version_url = "https://raw.githubusercontent.com/krvst/recon-filter/main/recon_filter/version.py"
        
    def _read_last_check(self) -> float:
        if self.state_file.exists():
            try:
                with self.state_file.open('r') as f:
                    data = json.load(f)
                    return data.get("last_check_time", 0.0)
            except (json.JSONDecodeError, KeyError):
                return 0.0
        return 0.0
        
    def _write_last_check(self):
        with self.state_file.open('w') as f:
            json.dump({"last_check_time": time.time()}, f)
            
    def _parse_version(self, text: str) -> str:
        for line in text.splitlines():
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
        return None

    def check_for_updates(self, force: bool = False, quiet: bool = False):
        """Asynchronously checks remote URL. Surpresses all network errors."""
        now = time.time()
        last_check = self._read_last_check()
        
        if not force and (now - last_check) < self.check_interval:
            return # Cached out
            
        try:
            req = urllib.request.Request(self.version_url, headers={'User-Agent': f'recon-filter/{__version__}'})
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    remote_text = response.read().decode('utf-8')
                    remote_version = self._parse_version(remote_text)
                    
                    self._write_last_check()
                    
                    if remote_version and remote_version != __version__:
                        # Basic string compare assumes semantic boundaries mapped properly natively
                        if not quiet:
                            console.print("\n[bold yellow]╭────────────────────────────────────────────────────────────╮[/bold yellow]")
                            console.print(f"[bold yellow]│[/bold yellow] A newer version of recon-filter is available: [bold cyan]v{remote_version}[/bold cyan]    [bold yellow]│[/bold yellow]")
                            console.print(f"[bold yellow]│[/bold yellow] You are currently using: [bold red]v{__version__}[/bold red]                         [bold yellow]│[/bold yellow]")
                            console.print(f"[bold yellow]│[/bold yellow] Please run [bold]recon-filter update[/bold] for instructions.         [bold yellow]│[/bold yellow]")
                            console.print("[bold yellow]╰────────────────────────────────────────────────────────────╯[/bold yellow]\n")

        except (urllib.error.URLError, Exception):
            pass # Fails silently over offline bounds
