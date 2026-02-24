"""
Execution bounds ensuring processes don't exceed memory vectors or traverse dangerous paths.
"""
import os
import psutil
from pathlib import Path
from typing import Optional

# Maximum permissible RAM extraction (bytes) before halt triggers - Defaults 2GB
MEMORY_CRITICAL_BYTES = 2 * 1024 * 1024 * 1024 

def enforce_memory_sandbox():
    """Validates the execution layer hasn't vastly exceeded physical hardware heuristics."""
    process = psutil.Process(os.getpid())
    current_memory = process.memory_info().rss
    
    if current_memory > MEMORY_CRITICAL_BYTES:
        raise MemoryError("Process Sandbox Exceeded: The filtering engine exceeded the safe RAM threshold and halted.")

def validate_path_traversal(target_path: Path, allowed_root: Optional[Path] = None):
    """
    Prevents Arbitrary Path Resolution (e.g. `../../../etc/passwd`).
    If allowed_root provided, strictly mandates paths live within it.
    """
    absolute_target = target_path.resolve()
    
    # Block systemic overrides if detected
    if str(absolute_target).startswith("/etc/") or str(absolute_target).startswith("/bin/"):
        raise PermissionError(f"Security Sandbox Denied: Unrestricted system directory targeted: {absolute_target}")
        
    if allowed_root:
        absolute_root = allowed_root.resolve()
        if not str(absolute_target).startswith(str(absolute_root)):
            raise PermissionError(f"Security Sandbox Denied: Path traversed outside trusted execution boundaries.")
