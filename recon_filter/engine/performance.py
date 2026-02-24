"""
Adaptive internal monitors tracking Resource thresholds flushing flows defensively.
"""
import os
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
from typing import Dict, Any

class PerformanceMonitor:
    def __init__(self, memory_limit_mb: int = None):
        if HAS_PSUTIL:
            self.pid = os.getpid()
            self.process = psutil.Process(self.pid)
            self.memory_limit_bytes = (memory_limit_mb * 1024 * 1024) if memory_limit_mb else None
        else:
            self.memory_limit_bytes = None
            if memory_limit_mb:
                import logging
                logging.getLogger("recon-filter").warning("Memory limits ignored: 'psutil' is not installed. Install with: pip install recon-filter[monitoring]")
                
        self.peak_memory = 0
        self.cpu_samples = []
    
    def heartbeat(self):
        """Samples current constraints pushing GC if limits crossed."""
        # Note: calling this per line is slow, so it should be called every X chunks
        if not HAS_PSUTIL:
            return
        mem_info = self.process.memory_info().rss
        if mem_info > self.peak_memory:
            self.peak_memory = mem_info
            
        self.cpu_samples.append(self.process.cpu_percent())
        
        if self.memory_limit_bytes and mem_info > self.memory_limit_bytes:
            # Force generational purge natively 
            import gc
            gc.collect()
            
    def generate_report(self) -> Dict[str, Any]:
        """Maps output analytics for the final diagnostics."""
        if not HAS_PSUTIL:
            return {
                "status": "monitoring_disabled",
                "message": "psutil not installed. Install with: pip install recon-filter[monitoring]"
            }
        avg_cpu = sum(self.cpu_samples) / max(len(self.cpu_samples), 1)
        
        return {
            "peak_memory_mb": round(self.peak_memory / (1024 * 1024), 2),
            "average_cpu_percent": round(avg_cpu, 2)
        }
