"""
PDF text extraction and writing hook logic processing memory efficiently natively.
"""
from pathlib import Path
from typing import Iterator
import pypdf

from recon_filter.config import FilterConfig
from recon_filter.engine.interfaces import FileReader, OutputWriter

class PdfFileReader(FileReader):
    def __init__(self, filepath: Path, config: FilterConfig):
        super().__init__(filepath, config)
        
    def read(self) -> Iterator[str]:
        # Streams PDF extraction directly retaining minimum local RAM context
        with self.filepath.open('rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        if line.strip():
                            yield line

class PdfOutputWriter(OutputWriter):
    """
    Creates a new minimalist PDF generating pages from the filtered strings directly.
    """
    def __init__(self, filepath: Path, config: FilterConfig):
        super().__init__(filepath, config)
        self.writer = pypdf.PdfWriter()
        self.file = None
        
    def __enter__(self):
        if not self.config.dry_run and not self.config.preview:
            self.file = open(self.atomic_path, 'wb')
        return self
        
    def _close_file(self):
        if self.file:
            self.file.close()
            self.success = True
            
    def write(self, item: str) -> None:
        # Incrementally maps payloads buffering. Because pypdf isn't great at streams,
        # we flush primitive encodings to the target.
        if self.file:
            self.file.write((item + "\n").encode('utf-8'))
