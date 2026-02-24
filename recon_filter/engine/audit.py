"""
Audit subsystem for writing non-repudiable execution tracking payloads.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path


from recon_filter.config import FilterConfig

class AuditLogger:
    """Writes strictly JSON formatted execution metadata to a central tracking log."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.audit_path = self.log_dir / "audit.log"
        
    def log_execution(self, target_file: Path, config: FilterConfig, matches: int, signature: str):
        """Append a new execution run metadata to the persistent audit list."""
        
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "target": str(target_file.absolute()),
            "filter_logic": {
                "keywords": config.keywords,
                "negative_keywords": config.exclude_keywords,
                "regex_pattern": config.regex_pattern,
                "logic_operator": config.match_logic,
            },
            "metrics": {
                "matches": matches,
                "hash_signature": signature
            },
            "flags": {
                "dry_run": config.dry_run,
                "safe_mode": config.safe_mode,
                "enforced_format": config.force_format
            }
        }
        
        # Append as a JSONL (JSON Lines) to avoid massive array parse overheads in huge logs
        with self.audit_path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
