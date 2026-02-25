"""
CLI filter module mapping inputs natively into the EngineProcessor.
"""
import time
import os
import json
import csv
import mimetypes
import concurrent.futures
from pathlib import Path
from typing import List, Optional

import typer
import questionary
from rich.console import Console
from rich.table import Table

from recon_filter.config import FilterConfig, ConfigManager
from recon_filter.engine.core import EngineProcessor
from recon_filter.engine.concurrency import ConcurrencyManager
from recon_filter.utils import setup_logger

app = typer.Typer()
console = Console()

def get_interactive_inputs(logger) -> tuple[List[Path], str, str]:
    """Uses Questionary to prompt user dynamically gracefully."""
    console.print("\n[bold yellow]Interactive Mode Engaged[/bold yellow] (Missing parameters detected)\n")
    
    target_dir = questionary.path(
        "Enter the directory or file path to scan:", 
        default="./"
    ).ask()
    
    if not target_dir:
        raise typer.Exit(code=1)
        
    pattern_type = questionary.select(
        "Select filter mechanism:",
        choices=[
            "Regex Pattern",
            "Keyword List (from file)",
            "Manual Keyword Entry",
            "Auto-Detect Processing (Process All)"
        ]
    ).ask()

    regex_pattern = ""
    keyword_file = ""

    if pattern_type == "Regex Pattern":
        regex_pattern = questionary.text("Enter your Regex pattern (e.g., ^ERROR):").ask()
    elif pattern_type == "Keyword List (from file)":
        keyword_file = questionary.path("Enter path to your keywords file:").ask()
    elif pattern_type == "Manual Keyword Entry":
        logger.warning("Manual Keyword Entry selected. We will save this to a temporary 'manual_keywords.txt'")
        manual_kws = questionary.text("Enter keywords separated by commas:").ask()
        if manual_kws:
            with open("manual_keywords.txt", "w") as f:
                for kw in manual_kws.split(","):
                    f.write(kw.strip() + "\n")
            keyword_file = "manual_keywords.txt"
    elif pattern_type == "Auto-Detect Processing (Process All)":
        logger.info("Executing Auto-Detect pipeline logic resolving all matching content natively.")

    return [Path(target_dir)], regex_pattern, keyword_file

def _expand_files(targets: List[Path], recursive: bool, excludes: List[str]) -> List[Path]:
    resolved_files = set()
    for target in targets:
        if target.is_dir():
            iterator = target.rglob("*") if recursive else target.iterdir()
            for path in iterator:
                if path.is_file():
                    resolved_files.add(path)
        elif target.is_file():
            resolved_files.add(target)
            
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

@app.command("filter", help="Execute the professional file filtering pipeline engine.")
def filter_cmd(
    files: Optional[List[Path]] = typer.Argument(None, help="Input files or directories to process."),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Load parameters from a YAML/JSON config file."),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory path (forces relative file creation)."),
    keyword_file: Optional[Path] = typer.Option(None, "--keyword-file", "-k", help="Path to keywords dictionary."),
    exclude_keyword_file: Optional[Path] = typer.Option(None, "--exclude-file", "-e", help="Negative filtering dict."),
    regex: Optional[str] = typer.Option(None, "--regex", "-r", help="Regex pattern matching."),
    
    # Engine Settings
    recursive: bool = typer.Option(False, "--recursive", "-R", help="Recursively scan directories."),
    exclude: List[str] = typer.Option([], "--exclude", help="Glob patterns to ignore (e.g., '*.map')."),
    match_logic: str = typer.Option("or", "--match-logic", help="Combinatorial logic: 'and' | 'or'."),
    no_duplicates: bool = typer.Option(False, "--no-duplicates", "-d", help="Strict duplicate removal hashing."),
    dedupe_scope: str = typer.Option("line", "--dedupe-scope", help="Deduplication scope: 'line' | 'normalized' | 'url-normalized'."),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Halt processing after N matches."),
    timeout: Optional[int] = typer.Option(None, "--timeout", "-t", help="Enforce maximum execution block time."),
    
    # Safety and Parsing Format Preservations
    force_format: Optional[str] = typer.Option(None, "--force-format", help="Override output formatting preservation bindings natively (txt, json, csv, pdf)."),
    encoding: Optional[str] = typer.Option(None, "--encoding", help="Manually enforce structural charset bindings."),
    safe_mode: bool = typer.Option(True, "--safe-mode/--no-safe-mode", help="Toggle Regex complexity checking and Sandbox bounds."),
    preview: bool = typer.Option(False, "--preview", "-p", help="Render first hits natively simulating matches without making IO replacements."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate pipeline without performing disk IO."),
    append: bool = typer.Option(False, "--append", "-a", help="Append to outputs instead of overwriting."),
    no_footer: bool = typer.Option(False, "--no-footer", help="Suppress final output file structural summary footers."),
    no_default_keyword: bool = typer.Option(False, "--no-default-keyword", help="Disable the default fallback recon dictionary."),
    
    # V4 Constraints
    memory_limit: Optional[int] = typer.Option(None, "--memory-limit", help="System RAM constraint limit matching (MB)."),
    max_workers: Optional[int] = typer.Option(None, "--max-workers", help="Max threaded execution loops mapping heavily."),
    no_parallel: bool = typer.Option(False, "--no-parallel", help="Force single-thread logic bypass."),
    safe_parallel: bool = typer.Option(False, "--safe-parallel", help="Adaptively bottleneck core limits mitigating massive parallel memory blocks conservatively."),
    adaptive_mode: bool = typer.Option(True, "--adaptive-mode/--no-adaptive-mode", help="Adaptive Thread pool bounds ensuring limits map flawlessly natively."),
    strict_performance: bool = typer.Option(False, "--strict-performance", help="Suppresses visual abstractions mapping fastest bounds."),
    enable_cache: bool = typer.Option(False, "--enable-cache", help="Skip unchanged SHA256 processing assets securely."),
    performance_report: bool = typer.Option(False, "--performance-report", help="Adds internal CPU/RAM mappings into local report logs."),
    
    # URL Validation & Analysis
    strict_url: bool = typer.Option(False, "--strict-url", help="Drop targets that are not cleanly formatted URLs."),
    allow_no_scheme: bool = typer.Option(False, "--allow-no-scheme", help="Auto-prepend 'http://' strictly to raw domains."),
    extract_params: bool = typer.Option(False, "--extract-params", help="Aggregate URL Parameter distributions."),
    param_report: bool = typer.Option(False, "--param-report", help="Generate dedicated 'parameters.json' cluster file."),
    
    # Clustering Flow
    group_by_ext: bool = typer.Option(False, "--group-by-extension", help="Dispatch matches categorically based on detected URL extensions."),
    group_by_depth: bool = typer.Option(False, "--group-by-depth", help="Dispatch matches categorically based on URL branch depths."),
    depth_limit: Optional[int] = typer.Option(None, "--depth-limit", help="Bound maximum depth generation arrays."),
    
    # Smart Filtering Engine
    smart_mode: bool = typer.Option(False, "--smart-mode", help="Activate intelligent scoring, fuzzy matching, and chain filtering."),
    priority_keyword: Optional[List[str]] = typer.Option(None, "--priority-keyword", help="Keywords boosted to maximum priority weight (repeatable)."),
    fuzzy_threshold: float = typer.Option(0.75, "--fuzzy-threshold", help="Fuzzy matching similarity threshold (0.0 - 1.0)."),

    # Auditing / Checksums
    no_backup: bool = typer.Option(False, "--no-backup", help="Disable structural source file backups."),
    backup_dir: Optional[str] = typer.Option(None, "--backup-dir", help="Shift backup `.bak` entities into isolated domains."),
    generate_hash_report: bool = typer.Option(False, "--generate-hash-report", help="Calculate contextual SHA256 integrity sums internally."),
    export_stats: Optional[str] = typer.Option(None, "--export-stats", help="Dump final statistics payload structurally to this JSON location."),
    report_format: str = typer.Option("json", "--report-format", help="Dictates structure of the exported metrics report (json/csv)."),
    
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose pipeline tracing."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Silence standard logs."),
):
    logger = setup_logger(verbose, quiet)
    
    # Professional Parameter Validation
    if not config_path and not files:
        files, regex, keyword_file = get_interactive_inputs(logger)
        
    try:
        # Resolve initial configurations globally
        if config_path:
            config = ConfigManager.load(config_path)
            # Apply CLI overrides if mapped natively
            if limit: config.match_limit = limit
            if timeout: config.timeout = timeout
            if dry_run: config.dry_run = dry_run
            if preview: config.preview = preview
            if append: config.append_mode = append
            if force_format: config.force_format = force_format
            if encoding: config.encoding = encoding
            logger.info(f"Configuration mappings established from payload: {config_path}")
        else:
            kws = []
            exc_kws = []
            if keyword_file and Path(keyword_file).exists():
                with Path(keyword_file).open('r') as f:
                    kws = [line.strip() for line in f if line.strip()]
            if exclude_keyword_file and exclude_keyword_file.exists():
                with exclude_keyword_file.open('r') as f:
                    exc_kws = [line.strip() for line in f if line.strip()]

            config = FilterConfig(
                keywords=kws,
                exclude_keywords=exc_kws,
                regex_pattern=regex,
                match_logic=match_logic,
                remove_duplicates=no_duplicates,
                dedupe_scope=dedupe_scope,
                match_limit=limit,
                timeout=timeout,
                safe_mode=safe_mode,
                force_format=force_format,
                encoding=encoding,
                memory_limit_mb=memory_limit,
                max_workers=max_workers,
                no_parallel=no_parallel,
                safe_parallel=safe_parallel,
                adaptive_mode=adaptive_mode,
                strict_performance=strict_performance,
                enable_cache=enable_cache,
                dry_run=dry_run,
                preview=preview,
                append_mode=append,
                no_footer=no_footer,
                no_default_keyword=no_default_keyword,
                export_stats_path=export_stats,
                report_format=report_format,
                no_backup=no_backup,
                backup_dir=backup_dir,
                generate_hash_report=generate_hash_report,
                performance_report=performance_report,
                strict_url=strict_url,
                allow_no_scheme=allow_no_scheme,
                extract_params=extract_params,
                param_report=param_report,
                group_by_extension=group_by_ext,
                group_by_depth=group_by_depth,
                depth_limit=depth_limit,
                smart_mode=smart_mode,
                priority_keywords=priority_keyword or [],
                fuzzy_threshold=fuzzy_threshold
            )
    except Exception as e:
        logger.error(f"Error: Configuration validation rejected: {e}")
        raise typer.Exit(1)

    # Resolution
    resolved_files = _expand_files(files, recursive, exclude)
    total_files = len(resolved_files)
    
    # ---------------------------------------------------------
    # Default Keyword Injector
    # ---------------------------------------------------------
    # Triggers strictly if no pattern was given and default bypass is inactive
    if not config.regex_pattern and not config.keywords and not config.no_default_keyword:
        config.keywords = FilterConfig.DEFAULT_RECON_KEYWORDS
        if verbose:
             logger.info("No matching rules detected -> Auto-loaded Default Recon Keywords for scanning.")

    # ---------------------------------------------------------
    # Mimetypes Smart Conflict Warning
    # ---------------------------------------------------------
    if verbose:
        for fpath in resolved_files:
             mtype, _ = mimetypes.guess_type(str(fpath))
             if mtype:
                 # Evaluate standard text bounds natively checking if binary extensions map incorrectly
                 if fpath.suffix.lower() == '.json' and 'json' not in mtype.lower():
                     logger.warning(f"Mimetype Mismatch Warning: {fpath.name} implies JSON but traces as {mtype}")
                 elif fpath.suffix.lower() == '.csv' and 'csv' not in mtype.lower():
                     logger.warning(f"Mimetype Mismatch Warning: {fpath.name} implies CSV but traces as {mtype}")
             
    if total_files == 0:
        logger.error("Error: Input files not found. Please verify the provided paths or directory recursions.")
        raise typer.Exit(1)

    # Output suppression during strict benchmarking targets natively
    visuals = not config.strict_performance and not quiet
    if visuals:
        logger.info(f"Target resolution complete. Initializing pipeline across {total_files} asset(s).")
    
    if config.dry_run:
        logger.info("[DRY RUN] Execution mode activated. Disk IO suspended safely.")
    if config.preview:
        logger.info("[PREVIEW] Interface mode activated. Memory caching outputs without modifications.")
        
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    start_time = time.time()
    
    global_stats = []
    total_lines = 0
    total_matches = 0
    
    # Map thread boundaries
    workers = ConcurrencyManager.resolve_optimal_workers(config.max_workers, config.no_parallel, config.safe_parallel)

    def process_file_bound(file_path: Path) -> dict:
        processor = EngineProcessor(file_path, output_dir, config)
        return processor.process()

    try:
        if workers == 1 or total_files == 1:
            # Synchronous explicit execution
            for file_path in resolved_files:
                stats = process_file_bound(file_path)
                global_stats.append(stats)
                total_lines += stats["lines_scanned"]
                total_matches += stats["matches_found"]
                
                if config.preview and stats.get("preview_buffer") and visuals:
                    console.print(f"\n[cyan]Preview Output Buffer: {file_path.name}[/cyan]")
                    for idx, buf in enumerate(stats["preview_buffer"]):
                        console.print(f"  {idx+1}: {buf.rstrip()}")
                    console.print("-" * 40)
        else:
            # Parallel Multi-Asset Logic Engine Mapping (Using Threads to avoid IPC payload lag on fast files)
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_file = {executor.submit(process_file_bound, f): f for f in resolved_files}
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        stats = future.result()
                        global_stats.append(stats)
                        total_lines += stats["lines_scanned"]
                        total_matches += stats["matches_found"]
                    except Exception as e:
                        logger.error(f"Error: Thread constraint logic failed on asset {file_path}: {e}")
                
    except Exception as e:
        logger.error(f"Error: Pipeline Critical Interruption: {e}")
        raise typer.Exit(1)

    elapsed = time.time() - start_time
    
    # Exporter Generation Pipeline
    if config.export_stats_path:
        export_path = Path(config.export_stats_path)
        payload = {
            "execution_ts": start_time,
            "aggregate_files": total_files,
            "aggregate_lines": total_lines,
            "aggregate_matches": total_matches,
            "execution_duration_sec": round(elapsed, 4),
            "safe_mode": config.safe_mode,
            "file_metrics": [ {k: v for k, v in s.items() if k != 'preview_buffer'} for s in global_stats ]
        }
        
        try:
            if config.report_format.lower() == 'csv':
                with export_path.open('w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=payload.keys())
                    writer.writeheader()
                    writer.writerow(payload)
            else:
                with export_path.open('w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=4)
            if visuals:
                logger.info(f"Analytics report generated locally: {config.export_stats_path}")
        except Exception as e:
            logger.error(f"Error: Analytics generation hook failed securely: {e}")

    # Final Execution Analysis Output
    if visuals:
        table = Table(title="Recon Filter Final Structural Statistics", style="green")
        table.add_column("Metric Component", style="cyan")
        table.add_column("Execution Value", style="magenta")
        
        table.add_row("Total Assets Digested", f"{total_files:,}")
        table.add_row("Total Sequence Lines Evaluated", f"{total_lines:,}")
        table.add_row("Net Stream Filtered Extractions", f"{total_matches:,}")
        table.add_row("Pipeline Processing Duration", f"{elapsed:.3f} seconds")
        
        console.print()
        console.print(table)
        
        if not dry_run and not preview:
            out_target = f"Directory '{output_dir}'" if output_dir else "Current Working Directory"
            console.print(f"\n[bold green]Execution Complete.[/bold green] Outputs secured within: [bold]{out_target}[/bold]")
