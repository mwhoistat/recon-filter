"""
Text Handler parsing raw unformatted buffers like `.log`, `.txt`, `.js`. preservation layer.
"""
from pathlib import Path
from typing import Iterator
import charset_normalizer

from recon_filter.config import FilterConfig
from recon_filter.engine.interfaces import FileReader, OutputWriter

class TextFileReader(FileReader):
    def __init__(self, filepath: Path, config: FilterConfig):
        super().__init__(filepath, config)
        self.encoding = self._detect_encoding()
        
    def _detect_encoding(self) -> str:
        if self.config.encoding:
            return self.config.encoding
            
        with self.filepath.open('rb') as f:
            raw = f.read(10000) # sample
        
        result = charset_normalizer.detect(raw)
        return result['encoding'] or 'utf-8'

    def read(self) -> Iterator[str]:
        # Utilizing generator natively for lines
        with self.filepath.open('r', encoding=self.encoding, errors='replace') as f:
            for line in f:
                yield line


class TextOutputWriter(OutputWriter):
    def __init__(self, filepath: Path, config: FilterConfig):
        super().__init__(filepath, config)
        self.file = None
        
    def __enter__(self):
        if not self.config.dry_run and not self.config.preview:
            # Writes straight into the atomic tmp block ensuring safety over interrupts
            self.file = open(self.atomic_path, 'w', encoding=self.config.encoding or 'utf-8')
        return self
        
    def _close_file(self):
        if self.file:
            self.file.close()
            self.success = True
            
    def write(self, item: str) -> None:
        if self.file:
            clean_item = item.rstrip('\r\n')
            self.file.write(clean_item + "\n")
