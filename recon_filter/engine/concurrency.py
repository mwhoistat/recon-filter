"""
Adaptive thread bounding ensuring hardware parity mapping.
"""
import psutil
from typing import Optional

class ConcurrencyManager:
    @staticmethod
    def resolve_optimal_workers(override_workers: Optional[int] = None, no_parallel: bool = False) -> int:
        """Determines CPU pools mapping max 70% natively."""
        if no_parallel:
            return 1
            
        if override_workers:
            return override_workers
            
        cores = psutil.cpu_count(logical=True) or 1
        
        # We target ~70% maximum extraction avoiding server lag spikes
        adaptive_limit = max(1, int(cores * 0.7))
        return adaptive_limit
        
    @staticmethod
    def should_stream_strictly(file_size_bytes: int, system_ram_bytes: int) -> bool:
        """Logic branch electing streaming mode vs memory arrays natively."""
        # If file is over 10% of total System RAM, stream aggressively.
        threshold = system_ram_bytes * 0.1
        return file_size_bytes > threshold
