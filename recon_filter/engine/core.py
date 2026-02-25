"""
Core orchestrator managing the Strategy Pattern resolution and file lifecycle dynamically.
"""
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Type, Optional, Tuple

from recon_filter.config import FilterConfig
from recon_filter.security.sandbox import enforce_memory_sandbox, validate_path_traversal
from recon_filter.security.integrity import calculate_sha256
from recon_filter.security.backup import execute_backup
from recon_filter.engine.filtering import RuleCompiler, apply_filters
from recon_filter.engine.audit import AuditLogger

from recon_filter.engine.cache import CacheManager
from recon_filter.version import __version__
from recon_filter.engine.performance import PerformanceMonitor
from recon_filter.engine.url_analyzer import UrlAnalyzer
from recon_filter.engine.smart_engine import SmartScorer

from recon_filter.engine.interfaces import FileProcessor, FileReader, OutputWriter
from recon_filter.engine.handlers.text_handler import TextFileReader, TextOutputWriter
from recon_filter.engine.handlers.json_handler import JsonFileReader, JsonOutputWriter
from recon_filter.engine.handlers.csv_handler import CsvFileReader, CsvOutputWriter
from recon_filter.engine.handlers.pdf_handler import PdfFileReader, PdfOutputWriter

class EngineProcessor(FileProcessor):
    def __init__(self, file_path: Path, output_dir: Optional[Path], config: FilterConfig):
        self.file_path = file_path
        self.output_dir = output_dir
        self.config = config
        self.audit = AuditLogger()
        self.cache = CacheManager()
        self.perf_monitor = PerformanceMonitor(memory_limit_mb=config.memory_limit_mb)
        self.url_analyzer = UrlAnalyzer(config)
        self.smart_scorer = None
        if config.smart_mode:
            self.smart_scorer = SmartScorer(
                priority_keywords=config.priority_keywords,
                fuzzy_threshold=config.fuzzy_threshold,
                custom_weights=config.keyword_scores if config.keyword_scores else None,
            )
        
    def _resolve_strategy(self) -> Tuple[Type[FileReader], Type[OutputWriter]]:
        """Maps target extensions or force configs to strict parsing engines."""
        ext = self.file_path.suffix.lower()
        if self.config.force_format:
            ext = f".{self.config.force_format.strip('.')}"
            
        if ext == '.json':
            return JsonFileReader, JsonOutputWriter
        elif ext == '.csv':
            return CsvFileReader, CsvOutputWriter
        elif ext == '.pdf':
            return PdfFileReader, PdfOutputWriter
        else:
            return TextFileReader, TextOutputWriter

    def process(self) -> Dict[str, Any]:
        """Lifecycle Executor wrapper. Manages backups, checksums, sandboxes, cache bindings, and IO filters strictly."""
        validate_path_traversal(self.file_path)
        enforce_memory_sandbox()
        
        start_time = time.time()
        timeout_deadline = start_time + self.config.timeout if self.config.timeout else None
        
        # 1. State integrity & Smart Caching
        hash_pre = calculate_sha256(self.file_path)
        
        if self.config.enable_cache and self.cache.is_cached(self.file_path, hash_pre):
            return {
                "file": self.file_path.name,
                "lines_scanned": 0,
                "matches_found": 0,
                "duration_seconds": 0.0,
                "hash_pre": hash_pre,
                "hash_post": hash_pre, # Unchanged native bounds
                "limit_reached": False,
                "skipped_cache": True,
                "performance": self.perf_monitor.generate_report()
            }
        
        # 2. Backups
        if not self.config.dry_run and not self.config.preview:
            execute_backup(self.file_path, self.config.no_backup, self.config.backup_dir)

        # 3. Output Resolution
        ReaderClass, WriterClass = self._resolve_strategy()
        
        out_ext = self.config.force_format if self.config.force_format else self.file_path.suffix.lower()
        if not out_ext:
            out_ext = '.txt'
        elif not out_ext.startswith('.'):
            out_ext = f".{out_ext}"
            
        out_name = f"{self.file_path.stem}_filtered{out_ext}"
        
        if self.output_dir:
            out_file = self.output_dir / out_name
        else:
            out_file = Path(out_name)

        # 4. Compiler Caching natively scoped
        compiled_regex = RuleCompiler.compile_regex(
            self.config.regex_pattern, 
            self.config.case_sensitive, 
            self.config.safe_mode
        )

        lines_scanned = 0
        matches_found = 0
        unique_matches = 0
        seen_hashes = set()
        preview_buffer = []
        
        reader = ReaderClass(self.file_path, self.config)
        is_clustering = self.config.group_by_extension or self.config.group_by_depth
        active_writers: Dict[str, OutputWriter] = {}
        
        def _get_writer_for_cluster(chunk: str) -> OutputWriter:
            if not is_clustering:
                return active_writers.get("default")
                
            cluster_key = "default"
            if self.config.group_by_extension:
                ext = self.url_analyzer.extract_extension(chunk)
                cluster_key = f"ext_{ext.strip('.')}"
            elif self.config.group_by_depth:
                depth = self.url_analyzer.extract_depth(chunk)
                cluster_key = f"depth_{depth}"
                
            if cluster_key not in active_writers:
                c_dir = self.output_dir if self.output_dir else Path(".")
                c_file = c_dir / f"{self.file_path.stem}_{cluster_key}{out_ext}"
                new_writer = WriterClass(c_file, self.config)
                new_writer.__enter__()
                if hasattr(reader, 'headers') and getattr(reader, 'headers', None):
                     new_writer.write(",".join(reader.headers))
                active_writers[cluster_key] = new_writer
                
            return active_writers[cluster_key]
        
        try:
            if self.config.preview:
                preview_limit = self.config.match_limit or 15
                
                if hasattr(reader, 'headers') and getattr(reader, 'headers', None):
                    pass
                    
                for idx, raw_chunk in enumerate(reader.read()):
                    if idx % 1000 == 0:
                        self.perf_monitor.heartbeat()
                    
                    if matches_found >= preview_limit:
                        break
                        
                    # Target URL validations natively
                    target_chunk = raw_chunk
                    if isinstance(raw_chunk, str):
                        is_valid_url, fixed_token = self.url_analyzer.analyze_token(str(raw_chunk))
                        if not is_valid_url:
                            continue # Strict URL filter drops this chunk
                        if fixed_token:
                            target_chunk = fixed_token
                        
                    is_match, score = apply_filters(target_chunk, self.config, compiled_regex, deadline=timeout_deadline)
                    lines_scanned += 1
                    
                    if is_match:
                        matches_found += 1
                        unique_matches += 1
                        preview_buffer.append(target_chunk)
            else:
                if not is_clustering:
                     default_w = WriterClass(out_file, self.config)
                     default_w.__enter__()
                     active_writers["default"] = default_w
                     if hasattr(reader, 'headers') and getattr(reader, 'headers', None):
                          default_w.write(",".join(reader.headers))

                for idx, raw_chunk in enumerate(reader.read()):
                    if idx % 1000 == 0:
                        self.perf_monitor.heartbeat()
                        
                    if self.config.match_limit and matches_found >= self.config.match_limit:
                        break
                        
                    # Target URL validations natively
                    target_chunk = raw_chunk
                    if isinstance(raw_chunk, str):
                        is_valid_url, fixed_token = self.url_analyzer.analyze_token(str(raw_chunk))
                        if not is_valid_url:
                            continue # Strict URL filter drops this chunk
                        if fixed_token:
                             target_chunk = fixed_token

                    is_match, score = apply_filters(target_chunk, self.config, compiled_regex, deadline=timeout_deadline)
                    lines_scanned += 1

                    # Smart scoring overlay: fuzzy + priority weights
                    if self.smart_scorer and isinstance(target_chunk, str):
                        smart_score, smart_matched = self.smart_scorer.score_line(
                            target_chunk, self.config.keywords
                        )
                        score += smart_score
                        if smart_matched and not is_match:
                            is_match = True  # Fuzzy match promoted this line
                    
                    if is_match:
                        is_duplicate = False
                        if self.config.remove_duplicates:
                            scope_target = str(target_chunk)
                            if self.config.dedupe_scope == 'normalized':
                                scope_target = scope_target.strip().lower()
                            elif self.config.dedupe_scope == 'url-normalized':
                                # Strips queries and fragments natively checking URLs purely
                                from urllib.parse import urlparse, urlunparse
                                try:
                                    p = urlparse(scope_target)
                                    scope_target = urlunparse((p.scheme, p.netloc, p.path, '', '', '')).lower()
                                except ValueError:
                                    scope_target = scope_target.strip().lower()

                            h = hash(scope_target)
                            if h in seen_hashes:
                                is_duplicate = True
                            seen_hashes.add(h)
                            
                        if not is_duplicate:
                            matches_found += 1
                            unique_matches += 1
                            writer = _get_writer_for_cluster(str(target_chunk))
                            writer.write(target_chunk)
                                
        except PermissionError:
            # Traps graceful permission blocks returning strict exit code without stack traces
            raise RuntimeError(f"Permission Denied. Please elevate user access for {self.file_path.name}")
        finally:
            # We explicitly trigger all active IO contextual teardowns ensuring atomic guarantees
            footer_lines = []
            if not self.config.no_footer and out_ext not in ['.json', '.csv']:
                ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                footer_lines = [
                    "",
                    f"Processed by recon-filter v{__version__}",
                    f"Total matches: {matches_found}",
                    f"Unique entries: {unique_matches}",
                    f"Generated at: {ts}"
                ]

            for c_writer in active_writers.values():
                if footer_lines and matches_found > 0:
                     for fl in footer_lines:
                         c_writer.write(fl)
                c_writer.success = True if matches_found > 0 else False
                c_writer.__exit__(None, None, None)
                
        # Handle Parameter Reports explicitly outside the cluster destructors
        if self.config.param_report or self.config.extract_params:
             import json
             p_path = (self.output_dir if self.output_dir else Path(".")) / "parameters.json"
             with p_path.open('w') as pf:
                 json.dump(self.url_analyzer.generate_report(), pf, indent=4)

        # 6. Post state integrity
        if self.config.preview or self.config.dry_run:
            hash_post = "unmodified"
        else:
            hash_post = calculate_sha256(out_file) if self.config.generate_hash_report else "disabled"
            if self.config.enable_cache:
                self.cache.update_cache(self.file_path, hash_pre)
        
        # 7. Auditing logs
        self.audit.log_execution(self.file_path, self.config, unique_matches, hash_post)

        duration = time.time() - start_time
        
        return {
            "file": self.file_path.name,
            "lines_scanned": lines_scanned,
            "matches_found": unique_matches,
            "duration_seconds": duration,
            "hash_pre": hash_pre,
            "hash_post": hash_post,
            "limit_reached": self.config.match_limit is not None and matches_found >= self.config.match_limit,
            "skipped_cache": False,
            "preview_buffer": preview_buffer,
            "performance": self.perf_monitor.generate_report(),
            "url_metrics": self.url_analyzer.generate_report() if (self.config.extract_params or self.config.param_report) else None
        }
