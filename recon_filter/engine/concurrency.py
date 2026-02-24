"""
Adaptive thread bounding ensuring hardware parity mapping.
"""
import os
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
from typing import Optional

class ConcurrencyManager:
    @staticmethod
    def resolve_optimal_workers(override_workers: Optional[int] = None, no_parallel: bool = False, safe_parallel: bool = False) -> int:
        """Determines CPU pools mapping max 70% natively."""
        if no_parallel:
            return 1
            
        if override_workers:
            return override_workers
            
        if HAS_PSUTIL:
            cores = psutil.cpu_count(logical=True) or 1
        else:
            cores = os.cpu_count() or 1
        
        # We target ~70% maximum extraction avoiding server lag spikes
        adaptive_limit = max(1, int(cores * 0.7))
        
        if safe_parallel:
            # Strictly limit to 2 or cores * 0.3 for pure backgrounding bounds avoiding RAM spikes
            safe_limit = max(1, int(cores * 0.3))
            return min(adaptive_limit, min(2, safe_limit))
            
        return adaptive_limit
        
    @staticmethod
    def should_stream_strictly(file_size_bytes: int, system_ram_bytes: int) -> bool:
        """Logic branch electing streaming mode vs memory arrays natively."""
        # If file is over 10% of total System RAM, stream aggressively.
        threshold = system_ram_bytes * 0.1
        return file_size_bytes > threshold
