"""
Benchmarking tools validating native Performance limits and Throughput logic.
"""
import time
import os
import tempfile
import json
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from recon_filter.config import FilterConfig
from recon_filter.engine.core import EngineProcessor
from recon_filter.utils import setup_logger

app = typer.Typer()
console = Console()

def generate_synthetic_payload(target_path: Path, mb_size: int = 100):
    """Writes a structural pseudo-log payload targeting MB constraints natively."""
    console.print(f"[cyan]Generating {mb_size}MB Benchmark Payload Dataset...[/cyan]")
    line = '2026-02-25 00:00:00 [INFO] System structural constraint validation routing check. CRITICAL sequence.\n'
    line_bytes = len(line.encode('utf-8'))
    target_lines = (mb_size * 1024 * 1024) // line_bytes
    
    with target_path.open('w') as f:
        for _ in range(target_lines):
            f.write(line)
            
    return target_lines

@app.command("benchmark", help="Engine load-testing measuring Throughput, Stream constraints, and IO mappings natively.")
def benchmark_cmd(
    size_mb: int = typer.Option(100, "--size", "-s", help="Target synthetic file bulk size (MB)."),
    regex: str = typer.Option("CRITICAL", "--regex", "-r", help="Regex matching parameter."),
    memory_limit: int = typer.Option(50, "--mem-limit", help="Strict psutil GC flushing bounds (MB)."),
    report: str = typer.Option("benchmark_report.json", "--report", help="Output analytical JSON trace."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose tracing."),
):
    logger = setup_logger(verbose)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        target_path = Path(tmp_dir) / "benchmark_payload.log"
        output_dir = Path(tmp_dir) / "output"
        os.makedirs(output_dir, exist_ok=True)
        
        total_lines = generate_synthetic_payload(target_path, size_mb)
        target_size_actual = target_path.stat().st_size / (1024 * 1024)
        
        config = FilterConfig(
            regex_pattern=regex,
            memory_limit_mb=memory_limit,
            performance_report=True,
            adaptive_mode=True,
            no_backup=True
        )
        
        processor = EngineProcessor(target_path, output_dir, config)
        
        console.print("[cyan]Executing V4 High-Performance Engine Processing Pipeline...[/cyan]")
        start_time = time.time()
        
        stats = processor.process()
        
        duration = time.time() - start_time
        lines_per_sec = total_lines / max(duration, 0.001)
        mb_per_sec = target_size_actual / max(duration, 0.001)
        
        table = Table(title="Recon-Filter V4 Engine Benchmarks")
        table.add_column("Metric Profile", style="cyan")
        table.add_column("Results", style="green")
        
        table.add_row("Synthetic File Size", f"{target_size_actual:.2f} MB")
        table.add_row("Lines Extracted", f"{stats['matches_found']:,} / {stats['lines_scanned']:,}")
        table.add_row("Execution Duration", f"{duration:.3f} s")
        table.add_row("Throughput (Lines/sec)", f"{lines_per_sec:,.0f} L/s")
        table.add_row("Throughput (MB/sec)", f"{mb_per_sec:.2f} MB/s")
        
        perf = stats.get("performance", {})
        table.add_row("Peak RAM Sandbox Memory", f"{perf.get('peak_memory_mb', 0):.2f} MB")
        table.add_row("Average CPU Thread Load", f"{perf.get('average_cpu_percent', 0):.2f} %")
        
        console.print()
        console.print(table)
        
        # Write analytics natively
        payload = {
            "version": "v4",
            "file_mb": target_size_actual,
            "throughput_lines_sec": lines_per_sec,
            "throughput_mb_sec": mb_per_sec,
            "duration": duration,
            "hardware_constraints": perf
        }
        with open(report, 'w') as f:
            json.dump(payload, f, indent=4)
            
        logger.info(f"Analytical pipeline footprint logged correctly to {report}")
