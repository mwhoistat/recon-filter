"""
Core orchestration logic for streaming and processing files, supporting multiprocessing and complex iterators.
"""
import os
import json
from pathlib import Path
from typing import Iterator, Iterable, Tuple, TextIO, Any, Set, List, Dict
import threading

from recon_filter.config import FilterConfig
from recon_filter.filters import apply_filters, compile_regex

def process_stream(
    file_stream: Iterable[str], 
    config: FilterConfig, 
    seen_hashes: Set[int]
) -> Iterator[Tuple[str, bool, bool]]:
    """
    Processes an iterable stream of lines (e.g., from a file) and applies logic.

    Yields:
        Tuple[str, bool, bool]: (Processed Line, Is Match, Is Duplicate)
    """
    compiled_regex = compile_regex(config.regex_pattern, config.case_sensitive)
    
    matches_found = 0

    for raw_line in file_stream:
        # Strict short circuit if the user-defined limits were hit
        if config.match_limit and matches_found >= config.match_limit:
            break

        line_content = raw_line.rstrip('\r\n')
        compare_line = line_content.strip() if config.strip_whitespace else line_content

        is_match, score = apply_filters(compare_line, config, compiled_regex)
        
        is_duplicate = False
        if is_match:
            if config.remove_duplicates:
                line_hash = hash(compare_line)
                if line_hash in seen_hashes:
                    is_duplicate = True
                else:
                    seen_hashes.add(line_hash)
            
            if not is_duplicate:
                matches_found += 1
                
        yield compare_line, is_match, is_duplicate


class ResultWriter:
    """
    Thread-safe contextual Result Writer natively supporting dry-runs and output file appends.
    """
    def __init__(self, filepath: str, config: FilterConfig):
        self.filepath = filepath
        self.config = config
        self.as_json = filepath.lower().endswith(".json")
        self.file: Optional[TextIO] = None
        self.first_item = True
        self._lock = threading.Lock()
        
    def __enter__(self) -> 'ResultWriter':
        if self.config.dry_run:
            return self

        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        mode = 'a' if self.config.append_mode else 'w'
        self.file = open(self.filepath, mode, encoding='utf-8')

        if self.as_json and not self.config.append_mode:
            self.file.write("[\n")
            
        return self
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.file and not self.config.dry_run:
            if self.as_json and not self.config.append_mode:
                self.file.write("\n]\n")
            self.file.close()

    def write(self, line: str) -> None:
        if self.config.dry_run:
            return

        if not self.file:
            raise RuntimeError("ResultWriter stream is not initialized.")

        with self._lock:
            if self.as_json:
                prefix = "  " if self.first_item else ",\n  "
                self.file.write(f'{prefix}{json.dumps(line)}')
                self.first_item = False
            else:
                self.file.write(line + "\n")


def expand_files(targets: List[Path], recursive: bool, excludes: List[str]) -> List[Path]:
    """
    Expands a list of paths recursively if configured, filtering out simple file extension glob excludes.
    """
    resolved_files = set()
    for target in targets:
        if target.is_dir():
            if recursive:
                for path in target.rglob("*"):
                    if path.is_file():
                        resolved_files.add(path)
            else:
                # Top level only
                for path in target.iterdir():
                    if path.is_file():
                        resolved_files.add(path)
        elif target.is_file():
            resolved_files.add(target)
            
    # Process simple excludes (e.g. "*.map")
    final_files = []
    for file in resolved_files:
        excluded = False
        for ex in excludes:
            if file.match(ex):
                excluded = True
                break
        if not excluded:
            final_files.append(file)
            
    return list(final_files)


def export_statistics(stats: Dict[str, Any], filepath: str) -> None:
    """Exports structured metrics payload to disk for downstream CI/CD."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)
