"""
CSV preservation layer keeping rows/column mappings intact natively.
"""
import csv
from pathlib import Path
from typing import Iterator

from recon_filter.config import FilterConfig
from recon_filter.engine.interfaces import FileReader, OutputWriter

class CsvFileReader(FileReader):
    def __init__(self, filepath: Path, config: FilterConfig):
        super().__init__(filepath, config)
        self.headers = None
        # Extract headers natively to prevent generator delay hooks
        with self.filepath.open('r', encoding=self.config.encoding or 'utf-8') as f:
            reader = csv.reader(f)
            try:
                self.headers = next(reader)
            except StopIteration:
                pass
        
    def read(self) -> Iterator[str]:
        with self.filepath.open('r', encoding=self.config.encoding or 'utf-8') as f:
            reader = csv.reader(f)
            try:
                # Skip the identical header from iteration
                next(reader)
            except StopIteration:
                pass
                
            for row in reader:
                # Process row identically to log string sequence incrementally
                yield ",".join(row)

class CsvOutputWriter(OutputWriter):
    def __init__(self, filepath: Path, config: FilterConfig):
        super().__init__(filepath, config)
        self.file = None
        self.writer = None
        self.headers_written = False
        
    def __enter__(self):
        if not self.config.dry_run and not self.config.preview:
            self.file = open(self.atomic_path, 'w', newline='', encoding=self.config.encoding or 'utf-8')
            self.writer = csv.writer(self.file)
        return self
        
    def _close_file(self):
        if self.file:
            self.file.close()
            self.success = True
            
    def write(self, item: str) -> None:
        if self.writer:
            row = item.split(",")
            self.writer.writerow(row)
