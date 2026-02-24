"""
CLI filter module mapping inputs natively into the EngineProcessor.
"""
import time
import os
import json
import csv
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

@app.command("filter", help="""Execute the professional file filtering pipeline engine.

recon-filter filter provides extreme stream processing over logs, payload dumps, and PDFs without consuming memory.
It automatically preserves structures (like JSON arrays and CSV fields).

Advanced URL Processing & Clustering (New in V1.0.0):
  By default, if URLs are detected, they are automatically validated.
  Use --extract-params to gather query parameters efficiently using O(1) memory counters.
  Use --cluster-extension or --cluster-depth to automatically generate subdirectories mapping routes cleanly.

Example Basic:
  recon-filter filter ./target.log -r "CRITICAL"
  
Example Advanced Clustering:
  recon-filter filter ./recon_data -r "https?://" --cluster-extension --extract-params
""")
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
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Halt processing after N matches."),
    timeout: Optional[int] = typer.Option(None, "--timeout", "-t", help="Enforce maximum execution block time."),
    
    # Safety and Parsing Format Preservations
    force_format: Optional[str] = typer.Option(None, "--force-format", help="Override output formatting preservation bindings natively (txt, json, csv, pdf)."),
    encoding: Optional[str] = typer.Option(None, "--encoding", help="Manually enforce structural charset bindings."),
    safe_mode: bool = typer.Option(True, "--safe-mode/--no-safe-mode", help="Toggle Regex complexity checking and Sandbox bounds."),
    preview: bool = typer.Option(False, "--preview", "-p", help="Render first hits natively simulating matches without making IO replacements."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate pipeline without performing disk IO."),
    append: bool = typer.Option(False, "--append", "-a", help="Append to outputs instead of overwriting."),
    
    # V4 Constraints
    memory_limit: Optional[int] = typer.Option(None, "--memory-limit", help="System RAM constraint limit matching (MB)."),
    max_workers: Optional[int] = typer.Option(None, "--max-workers", help="Max threaded execution loops mapping heavily."),
    no_parallel: bool = typer.Option(False, "--no-parallel", help="Force single-thread logic bypass."),
    adaptive_mode: bool = typer.Option(True, "--adaptive-mode/--no-adaptive-mode", help="Adaptive Thread pool bounds ensuring limits map flawlessly natively."),
    strict_performance: bool = typer.Option(False, "--strict-performance", help="Suppresses visual abstractions mapping fastest bounds."),
    enable_cache: bool = typer.Option(False, "--enable-cache", help="Skip unchanged SHA256 processing assets securely."),
    performance_report: bool = typer.Option(False, "--performance-report", help="Adds internal CPU/RAM mappings into local report logs."),
    
    # Auditing / Checksums
    no_backup: bool = typer.Option(False, "--no-backup", help="Disable structural source file backups."),
    backup_dir: Optional[str] = typer.Option(None, "--backup-dir", help="Shift backup `.bak` entities into isolated domains."),
    generate_hash_report: bool = typer.Option(False, "--generate-hash-report", help="Calculate contextual SHA256 integrity sums internally."),
    export_stats: Optional[str] = typer.Option(None, "--export-stats", help="Dump final statistics payload structurally to this JSON location."),
    report_format: str = typer.Option("json", "--report-format", help="Dictates structure of the exported metrics report (json/csv)."),
    
    # URL Processing & Clustering
    url_mode: bool = typer.Option(False, "--url-mode", help="Force active URL validation (RFC compliant)."),
    no_url_validate: bool = typer.Option(False, "--no-url-validate", help="Disable automatic URL validation if patterns look like URLs."),
    extract_params: bool = typer.Option(False, "--extract-params", help="Extract URL query parameters to parameter_summary.json incrementally."),
    cluster_extension: bool = typer.Option(False, "--cluster-extension", help="Create output directories based on URL/Path extensions (e.g. js/, png/)."),
    cluster_depth: bool = typer.Option(False, "--cluster-depth", help="Create output directories clustering targets by path depth (e.g. depth_3/)."),
    
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
                match_limit=limit,
                timeout=timeout,
                safe_mode=safe_mode,
                force_format=force_format,
                encoding=encoding,
                memory_limit_mb=memory_limit,
                max_workers=max_workers,
                no_parallel=no_parallel,
                adaptive_mode=adaptive_mode,
                strict_performance=strict_performance,
                enable_cache=enable_cache,
                dry_run=dry_run,
                preview=preview,
                append_mode=append,
                export_stats_path=export_stats,
                report_format=report_format,
                no_backup=no_backup,
                backup_dir=backup_dir,
                generate_hash_report=generate_hash_report,
                performance_report=performance_report,
                url_mode=url_mode,
                no_url_validate=no_url_validate,
                extract_params=extract_params,
                cluster_extension=cluster_extension,
                cluster_depth=cluster_depth
            )
    except Exception as e:
        logger.error(f"Error: Configuration validation rejected: {e}")
        raise typer.Exit(1)

    # Resolution
    resolved_files = _expand_files(files, recursive, exclude)
    total_files = len(resolved_files)
    
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
    workers = ConcurrencyManager.resolve_optimal_workers(config.max_workers, config.no_parallel)

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
    
    # ----------------------------------------------------
    # V1.0.0 Unified Analyzer Reporting
    # ----------------------------------------------------
    if config.extract_params:
        from collections import Counter
        global_params = Counter()
        total_urls = 0
        for s in global_stats:
            global_params.update(s.get("param_stats", {}))
            total_urls += s.get("urls_analyzed", 0)
            
        if global_params:
            most_common = global_params.most_common(10)
            payload = {
                "total_urls_analyzed_for_params": total_urls,
                "total_unique_parameters": len(global_params),
                "top_10_most_frequent_parameters": [{"parameter": k, "frequency": v} for k, v in most_common],
                "complete_frequency_distribution": dict(global_params)
            }
            param_out = (output_dir / "parameter_summary.json") if output_dir else Path("parameter_summary.json")
            try:
                with param_out.open('w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=4)
                if visuals: logger.info(f"URL Parameter statistics generated: {param_out}")
            except IOError as e:
                logger.error(f"Failed to write parameter summary: {e}")

    if config.cluster_depth:
        from collections import Counter
        global_depth = Counter()
        total_cluster = 0
        for s in global_stats:
            global_depth.update(s.get("depth_stats", {}))
            total_cluster += s.get("cluster_lines", 0)
            
        if global_depth:
            depth_out = (output_dir / "depth_clustering_summary.txt") if output_dir else Path("depth_clustering_summary.txt")
            try:
                with depth_out.open('w', encoding='utf-8') as f:
                    f.write("Recon-Filter Depth Clustering Summary\n")
                    f.write("="*40 + "\n")
                    f.write(f"Total entries processed: {total_cluster}\n\n")
                    
                    most_common = global_depth.most_common(1)
                    if most_common:
                        f.write(f"Most common depth: {most_common[0][0]} ({most_common[0][1]} lines)\n\n")
                    
                    f.write("Depth Distribution:\n")
                    for depth, count in global_depth.most_common():
                         f.write(f"  - {depth}: {count} hits\n")
                if visuals: logger.info(f"Path Depth Clustering summary generated: {depth_out}")
            except IOError as e:
                logger.error(f"Failed to write depth summary: {e}")
                
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
