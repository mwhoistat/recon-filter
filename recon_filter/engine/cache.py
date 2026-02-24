"""
Smart execution caching tracking SHA256 target validity averting redundant cycles natively.
"""
import json
import os
from pathlib import Path
from typing import Dict

class CacheManager:
    """Manages lightweight state caches determining if files mandate re-processing."""
    
    def __init__(self, cache_dir: str = ".recon_cache"):
        self.cache_dir = Path(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.state_file = self.cache_dir / "hash_state.json"
        
    def _load_cache(self) -> Dict[str, str]:
        if self.state_file.exists():
            try:
                with self.state_file.open('r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
        
    def _save_cache(self, state: Dict[str, str]):
        with self.state_file.open('w') as f:
            json.dump(state, f, indent=2)

    def is_cached(self, filepath: Path, current_hash: str) -> bool:
        """Determines if the payload matches the last cached mapping securely."""
        state = self._load_cache()
        target = str(filepath.resolve())
        return state.get(target) == current_hash

    def update_cache(self, filepath: Path, final_hash: str):
        """Logs the target resolution footprint updating the caching directory natively."""
        state = self._load_cache()
        target = str(filepath.resolve())
        state[target] = final_hash
        self._save_cache(state)
        
    def purge(self):
        """Destroys cache definitions totally."""
        if self.cache_dir.exists():
            import shutil
            shutil.rmtree(self.cache_dir)
