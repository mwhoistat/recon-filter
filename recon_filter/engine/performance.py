"""
Adaptive internal monitors tracking Resource thresholds flushing flows defensively.
"""
import os
import psutil
from typing import Dict, Any

class PerformanceMonitor:
    def __init__(self, memory_limit_mb: int = None):
        self.pid = os.getpid()
        self.process = psutil.Process(self.pid)
        self.memory_limit_bytes = (memory_limit_mb * 1024 * 1024) if memory_limit_mb else None
        
        self.peak_memory = 0
        self.cpu_samples = []
    
    def heartbeat(self):
        """Samples current constraints pushing GC if limits crossed."""
        # Note: calling this per line is slow, so it should be called every X chunks
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
        avg_cpu = sum(self.cpu_samples) / max(len(self.cpu_samples), 1)
        
        return {
            "peak_memory_mb": round(self.peak_memory / (1024 * 1024), 2),
            "average_cpu_percent": round(avg_cpu, 2)
        }
