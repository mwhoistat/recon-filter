"""
Automatic file backup subsystem ensuring destructive overwrite states are fully recoverable.
"""
import shutil
import os
from pathlib import Path
from typing import Optional

def execute_backup(source_path: Path, no_backup: bool = False, custom_dir: Optional[str] = None) -> Optional[Path]:
    """
    Safely creates a backup artifact of the target input file dynamically before modification runs.
    """
    if no_backup:
        return None
        
    if not source_path.exists():
        return None
        
    # Resolution targets
    if custom_dir:
        backup_dir = Path(custom_dir)
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = backup_dir / f"{source_path.name}.bak"
    else:
        backup_path = Path(str(source_path) + ".bak")
        
    try:
        shutil.copy2(source_path, backup_path)
        return backup_path
    except Exception as e:
        raise PermissionError(f"Backup subsystem failed to secure artifact resulting in halted execution stream: {e}")
