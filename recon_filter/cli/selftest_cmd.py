"""
Automated Self-Test subcommand generating dummy entities routing natively ensuring library stability.
"""
import tempfile
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from recon_filter.config import FilterConfig
from recon_filter.engine.core import EngineProcessor

app = typer.Typer()
console = Console()

def _run_test(name: str, test_func) -> bool:
    """Executes a bound callable trapping execution fragments natively."""
    try:
        test_func()
        return True
    except Exception as e:
        console.print(f"[red]Error mapping {name}: {e}[/red]")
        return False

@app.command("self-test", help="Excercises all Strategy Core systems locally guaranteeing system parity.")
def selftest_cmd():
    console.print("\n[cyan]Initializing V1.0.0 System Parity Core Self-Tests...[/cyan]")
    
    results = {}
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # 1. Text Parsing
        def test_text():
            src = tmp_path / "test.txt"
            src.write_text("Hello\nCRITICAL fail\nWORLD\n")
            cfg = FilterConfig(regex_pattern="CRITICAL", no_backup=True)
            Processor = EngineProcessor(src, tmp_path, cfg)
            stats = Processor.process()
            tgt = tmp_path / "test_filtered.txt"
            assert stats["matches_found"] == 1
            assert "CRITICAL" in tgt.read_text()
            
        results["Text IO Handlers"] = _run_test("Text IO Handlers", test_text)
        
        # 2. JSON Stream Parity
        def test_json():
            src = tmp_path / "test.json"
            src.write_text('[{"id": 1, "log": "ERROR"}, {"id": 2, "log": "INFO"}]')
            cfg = FilterConfig(regex_pattern="ERROR", no_backup=True)
            Processor = EngineProcessor(src, tmp_path, cfg)
            stats = Processor.process()
            tgt = tmp_path / "test_filtered.json"
            import json
            data = json.loads(tgt.read_text())
            assert len(data) == 1
            assert stats["matches_found"] == 1
            
        results["JSON stream ijson mappings"] = _run_test("JSON stream ijson mappings", test_json)
        
        # 3. Cache Systems
        def test_cache():
            src = tmp_path / "target.txt"
            src.write_text("A\nB\n")
            cfg_cache = FilterConfig(regex_pattern="A", enable_cache=True, no_backup=True)
            
            from recon_filter.engine.cache import CacheManager
            cacher = CacheManager(cache_dir=str(tmp_path / ".test_cache"))
            
            p1 = EngineProcessor(src, tmp_path, cfg_cache)
            p1.cache = cacher # Bind manual mapping
            s1 = p1.process()
            assert not s1["skipped_cache"]
            
            p2 = EngineProcessor(src, tmp_path, cfg_cache)
            p2.cache = cacher
            s2 = p2.process()
            assert s2["skipped_cache"]
            
        results["Engine Signature Caching"] = _run_test("Engine Signature Caching", test_cache)

    table = Table(title="Recon-Filter Production Diagnostics")
    table.add_column("Subsystem Test Component")
    table.add_column("Result Status")
    
    all_passed = True
    for test_name, status in results.items():
        if status:
             table.add_row(test_name, "[bold green]PASS[/bold green]")
        else:
             table.add_row(test_name, "[bold red]FAIL[/bold red]")
             all_passed = False
             
    console.print()
    console.print(table)
    
    if all_passed:
        console.print("\n[bold green]All Core Subsystems Operational. The Pipeline is ready for Distribution.[/bold green]")
        raise typer.Exit(0)
    else:
        console.print("\n[bold red]System Instability Detected. Please check environments.[/bold red]")
        raise typer.Exit(1)
