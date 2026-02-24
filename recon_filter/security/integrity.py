"""
SHA-256 state tracking for auditing inputs natively.
"""
import hashlib
from pathlib import Path

def calculate_sha256(filepath: Path) -> str:
    """
    Calculates SHA-256 for physical files chunk-by-chunk preserving system memory buffers.
    Returns empty string if target missing or unreadable.
    """
    if not filepath.exists() or not filepath.is_file():
        return ""
        
    sha256_hash = hashlib.sha256()
    try:
        with filepath.open("rb") as f:
            # Digest 4K blocks 
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return "integrity_check_failed"
