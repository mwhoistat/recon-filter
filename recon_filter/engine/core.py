"""
Core orchestrator managing the Strategy Pattern resolution and file lifecycle dynamically.
"""
import time
from pathlib import Path
from typing import Dict, Any, Type, Optional, Tuple

from recon_filter.config import FilterConfig
from recon_filter.security.sandbox import enforce_memory_sandbox, validate_path_traversal
from recon_filter.security.integrity import calculate_sha256
from recon_filter.security.backup import execute_backup
from recon_filter.engine.filtering import RuleCompiler, apply_filters
from recon_filter.engine.audit import AuditLogger

from recon_filter.engine.analyzers.url_processor import URLProcessor
from recon_filter.engine.analyzers.param_extractor import ParameterExtractor
from recon_filter.engine.analyzers.cluster_engine import ClusterEngine

from recon_filter.engine.cache import CacheManager
from recon_filter.engine.performance import PerformanceMonitor

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
        
        param_ext = ParameterExtractor(self.output_dir) if self.config.extract_params else None
        cluster_eng = ClusterEngine(self.output_dir, self.config.cluster_extension, self.config.cluster_depth) if (self.config.cluster_extension or self.config.cluster_depth) else None
        invalid_urls_path = self.output_dir / "invalid_urls.log" if self.output_dir else Path("invalid_urls.log")
        
        reader = ReaderClass(self.file_path, self.config)
        
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
                        
                    is_match, score = apply_filters(raw_chunk, self.config, compiled_regex, deadline=timeout_deadline)
                    lines_scanned += 1
                    
                    if is_match:
                        matches_found += 1
                        unique_matches += 1
                        preview_buffer.append(raw_chunk)
            else:
                with WriterClass(out_file, self.config) as writer:
                    if hasattr(reader, 'headers') and getattr(reader, 'headers', None):
                        writer.write(",".join(reader.headers))
                        
                    for idx, raw_chunk in enumerate(reader.read()):
                        if idx % 1000 == 0:
                            self.perf_monitor.heartbeat()
                        
                        if self.config.match_limit and matches_found >= self.config.match_limit:
                            break

                        is_match, score = apply_filters(raw_chunk, self.config, compiled_regex, deadline=timeout_deadline)
                        lines_scanned += 1
                        
                        if is_match:
                            is_duplicate = False
                            if self.config.remove_duplicates:
                                h = hash(raw_chunk)
                                if h in seen_hashes:
                                    is_duplicate = True
                                seen_hashes.add(h)
                                
                            if not is_duplicate:
                                matches_found += 1
                                unique_matches += 1
                                writer.write(raw_chunk)
                                
                                # Analyzer Integrations
                                content = raw_chunk.strip()
                                if self.config.url_mode or (not self.config.no_url_validate and URLProcessor.looks_like_url(content)):
                                    if not URLProcessor.is_valid_url(content):
                                        try:
                                            with invalid_urls_path.open('a', encoding='utf-8') as f:
                                                f.write(content + "\n")
                                        except IOError:
                                            pass
                                    elif param_ext:
                                        param_ext.extract(content)
                                        
                                if cluster_eng:
                                    cluster_eng.process(content)
                                
        except PermissionError:
            # Traps graceful permission blocks returning strict exit code without stack traces
            raise RuntimeError(f"Permission Denied. Please elevate user access for {self.file_path.name}")
        except Exception as e:
            raise RuntimeError(f"Engine Failure on {self.file_path.name}: {e}")

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
            "param_stats": dict(param_ext.param_counter) if param_ext else {},
            "urls_analyzed": param_ext.total_urls_processed if param_ext else 0,
            "depth_stats": dict(cluster_eng.depth_counter) if cluster_eng else {},
            "cluster_lines": cluster_eng.total_clustered if cluster_eng else 0
        }
