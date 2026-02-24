"""
Configuration classes and managers for the recon-filter v4.
Supports streaming constraints, adaptive concurrency, caching, and atomic monitoring.
"""
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict
import yaml

@dataclass
class FilterConfig:
    """
    Holds configuration settings for the filtering operations natively.
    """
    # Core Pattern rules
    keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    regex_pattern: Optional[str] = None
    
    # Matching modifiers
    case_sensitive: bool = False
    match_logic: str = "or"  # "and" | "or"
    remove_duplicates: bool = False
    strip_whitespace: bool = False
    min_length: int = 0
    max_length: Optional[int] = None
    min_score: int = 0
    keyword_scores: Dict[str, int] = field(default_factory=dict)
    
    # Advanced limits & safety
    match_limit: Optional[int] = None
    timeout: Optional[int] = None
    safe_mode: bool = False
    
    # File Encoding & Formatting
    force_format: Optional[str] = None
    encoding: Optional[str] = None
    
    # V4 Resource & Concurrency Optimization
    memory_limit_mb: Optional[int] = None
    max_workers: Optional[int] = None
    no_parallel: bool = False
    adaptive_mode: bool = True
    strict_performance: bool = False
    enable_cache: bool = False
    
    # Security & Execution Modifiers
    dry_run: bool = False
    preview: bool = False
    append_mode: bool = False
    
    # Reporting & Auditing
    export_stats_path: Optional[str] = None
    report_format: str = "json" # "json" | "csv"
    no_backup: bool = False
    backup_dir: Optional[str] = None
    generate_hash_report: bool = False
    performance_report: bool = False
    
    # URL & Cluster Engines
    strict_url: bool = False
    allow_no_scheme: bool = False
    extract_params: bool = False
    param_report: bool = False
    group_by_extension: bool = False
    group_by_depth: bool = False
    depth_limit: Optional[int] = None

    def __post_init__(self):
        self.match_logic = self.match_logic.lower()
        if self.match_logic not in ["and", "or"]:
            raise ValueError("match_logic must be 'and' or 'or'")


class ConfigManager:
    """
    Handles saving and loading of `FilterConfig` directly from JSON/YAML structures.
    """
    
    @staticmethod
    def load(filepath: Path) -> FilterConfig:
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file {filepath} not found.")

        ext = filepath.suffix.lower()
        with filepath.open('r', encoding='utf-8') as f:
            if ext in ['.yaml', '.yml']:
                data = yaml.safe_load(f) or {}
            elif ext == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration extension '{ext}'. Use .yaml or .json.")

        return FilterConfig(**data)

    @staticmethod
    def save(config: FilterConfig, filepath: Path) -> None:
        ext = filepath.suffix.lower()
        data = asdict(config)
        
        with filepath.open('w', encoding='utf-8') as f:
            if ext in ['.yaml', '.yml']:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            elif ext == '.json':
                json.dump(data, f, indent=4)
            else:
                raise ValueError(f"Unsupported extension '{ext}'.")

    @staticmethod
    def generate_default(filepath: Path) -> None:
        default_config = FilterConfig(
            keywords=["admin", "root", "password"],
            exclude_keywords=["false_positive"],
            regex_pattern="^CRITICAL|^ERROR",
            case_sensitive=False,
            match_logic="or",
            remove_duplicates=True,
            safe_mode=True,
            adaptive_mode=True,
            strict_url=False,
            allow_no_scheme=False,
            extract_params=False,
            param_report=False,
            group_by_extension=False,
            group_by_depth=False,
            depth_limit=None
        )
        ConfigManager.save(default_config, filepath)
