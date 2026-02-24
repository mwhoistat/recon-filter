"""
Command Line Interface handler for recon-filter.
"""
import time
from pathlib import Path
from typing import List, Optional, Set

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TextColumn, BarColumn
from rich.table import Table

from recon_filter.config import FilterConfig
from recon_filter.core import process_stream, ResultWriter
from recon_filter.utils import setup_logger

# Initialize application orchestrators
app = typer.Typer(
    name="recon-filter",
    help="Professional CLI tool to filter lines based on keywords or regex patterns.",
    add_completion=False,
)
console = Console()


def load_keywords(filepath: Path, logger) -> List[str]:
    """Loads a list of keywords uniformly from a file mapping."""
    if not filepath.exists():
        logger.error(f"Keyword file not found: {filepath}")
        raise typer.Exit(code=1)

    with filepath.open('r', encoding='utf-8', errors='replace') as f:
        # Ignore empty lines strictly
        return [line.strip() for line in f if line.strip()]


@app.command()
def filter(
    files: List[Path] = typer.Argument(
        ...,
        help="Input files to process (supports shell wildcards natively like *.log)."
    ),
    output: Path = typer.Option(
        ...,
        "--output", "-o",
        help="Output file path (supports standard .txt or JSON formats natively)."
    ),
    keyword_file: Optional[Path] = typer.Option(
        None,
        "--keyword-file", "-k",
        help="Path to file containing exact keyword sequences."
    ),
    regex: Optional[str] = typer.Option(
        None,
        "--regex", "-r",
        help="Regular expression pattern. Only lines matching will pass."
    ),
    case_sensitive: bool = typer.Option(
        False,
        "--case-sensitive", "-c",
        help="Enable case-sensitive matching for both regex and keywords."
    ),
    match_logic: str = typer.Option(
        "or",
        "--match-logic",
        help="Logic constraint between multiple keywords/regex ('and' / 'or')."
    ),
    no_duplicates: bool = typer.Option(
        False,
        "--no-duplicates", "-d",
        help="Strict duplicate removal across all processed outputs based on hashing."
    ),
    strip_whitespace: bool = typer.Option(
        False,
        "--strip", "-s",
        help="Strip leading and trailing whitespace from lines prior to evaluating."
    ),
    min_length: int = typer.Option(
        0,
        "--min-length",
        help="Minimum required sequence character length."
    ),
    max_length: Optional[int] = typer.Option(
        None,
        "--max-length",
        help="Maximum allowed sequence character length."
    ),
    min_score: int = typer.Option(
        0,
        "--min-score",
        help="Minimum cumulative score threshold. Required keyword score mappings."
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable diagnostic trace logging."
    )
):
    """
    Executes professional-grade file filtering line-by-line via stream-processing.
    """
    logger = setup_logger(verbose)
    start_time = time.time()

    if not keyword_file and not regex:
        logger.warning(
            "No core filter conditions (keywords or regex) were provided. "
            "Will effectively mirror input to output modulo other constraints."
        )

    keywords = load_keywords(keyword_file, logger) if keyword_file else []

    try:
        config = FilterConfig(
            keywords=keywords,
            regex_pattern=regex,
            case_sensitive=case_sensitive,
            match_logic=match_logic,
            remove_duplicates=no_duplicates,
            strip_whitespace=strip_whitespace,
            min_length=min_length,
            max_length=max_length,
            min_score=min_score,
            keyword_scores={}
        )
    except ValueError as e:
        logger.error(f"Configuration Initialization Error: {e}")
        raise typer.Exit(code=1)

    total_files = len(files)
    logger.info(f"Loaded constraints successfully. Targeting {total_files} file(s)...")

    # Metrics Accumulators
    total_lines = 0
    total_matches = 0
    unique_matches = 0
    seen_hashes: Set[int] = set()

    # Launch Rich Progress Tracker UI
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        
        main_task = progress.add_task(f"[cyan]Orchestrating Pipeline...", total=total_files)

        try:
            with ResultWriter(str(output)) as writer:
                for idx, file_path in enumerate(files):
                    if not file_path.exists() or not file_path.is_file():
                        logger.warning(f"File target invalidated (not found): {file_path}")
                        progress.advance(main_task)
                        continue
                    
                    progress.update(
                        main_task,
                        description=f"[cyan]Scanning -> {file_path.name} ({idx+1}/{total_files})"
                    )

                    with file_path.open('r', encoding='utf-8', errors='replace') as infile:
                        for line, is_match, is_duplicate in process_stream(infile, config, seen_hashes):
                            total_lines += 1
                            if is_match:
                                total_matches += 1
                                if not is_duplicate:
                                    unique_matches += 1
                                    writer.write(line)
                                    
                    progress.advance(main_task)
                    
        except RuntimeError as e:
            logger.error(f"Stream Context Runtime Error: {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            logger.error(f"Unexpected termination: {e}")
            raise typer.Exit(code=1)

    elapsed = time.time() - start_time
    logger.info("Job successfully completed.")

    # Render post-execution analysis metrics natively
    table = Table(title="Recon Filter Final Statistics", style="green")
    
    table.add_column("Metric Profile", style="cyan", no_wrap=True)
    table.add_column("Value / Indicator", style="magenta")
    
    table.add_row("Total Files Digested", f"{total_files:,}")
    table.add_row("Total Lines Scanned", f"{total_lines:,}")
    table.add_row("Gross Filter Matches", f"{total_matches:,}")
    
    if no_duplicates:
        table.add_row("Net Deduplicated Output", f"{unique_matches:,}")
        table.add_row("Duplicate Redundancies Detached", f"{total_matches - unique_matches:,}")
    else:
        table.add_row("Net Stream Output Written", f"{total_matches:,}")
        
    table.add_row("Total Job Time Duration", f"{elapsed:.3f} seconds")
    
    console.print()
    console.print(table)
    console.print(f"\n[bold green]Success![/bold green] Results securely deposited in: [bold]{output}[/bold]")
