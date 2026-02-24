"""
Abstract Base Classes establishing the Strategy Patterns for recon-filter.
Includes V4 atomic IO and lazy generator stream enforcements entirely.
"""
from abc import ABC, abstractmethod
from typing import Iterator, Any, Dict
from pathlib import Path
import os
import shutil

from recon_filter.config import FilterConfig


class FileReader(ABC):
    """Strategy for parsing raw inputs into processable entities (lines/rows)."""
    
    @abstractmethod
    def __init__(self, filepath: Path, config: FilterConfig):
        self.filepath = filepath
        self.config = config

    @abstractmethod
    def read(self) -> Iterator[Any]:
        """Yields raw parsed chunks suitable for the FilterEngine natively as generators."""
        pass


class OutputWriter(ABC):
    """Strategy for securely writing the payload back via Atomic swaps natively."""
    
    def __init__(self, filepath: Path, config: FilterConfig):
        self.filepath = filepath
        self.config = config
        self.atomic_path = Path(f"{filepath}.tmp")
        self.success = False

    @abstractmethod
    def __enter__(self):
        """Must open IO mapping towards self.atomic_path safely."""
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Abstract core enforcing Atomic I/O Commit.
        If an exception occurred, we unlink the temp fragment ensuring no corrupt partials exist natively.
        If successful, we strictly swap the temp file over the targeted canonical output natively.
        """
        self._close_file()
        
        if self.config.dry_run or self.config.preview:
             return
             
        if exc_type is None and self.success:
            # Atomic commit successfully overrides Target
            if self.atomic_path.exists():
                if self.config.append_mode and self.filepath.exists():
                    # If append mode natively, we concatenate the tmp file safely into target
                    with self.filepath.open('ab') as target, self.atomic_path.open('rb') as tmp:
                        shutil.copyfileobj(tmp, target)
                    self.atomic_path.unlink()
                else:
                    os.replace(self.atomic_path, self.filepath)
        else:
            # Abort/Exception natively destroying fragments
            if self.atomic_path.exists():
                self.atomic_path.unlink()
                
    @abstractmethod
    def _close_file(self):
        """Child classes must override to close the open handle safely."""
        pass

    @abstractmethod
    def write(self, item: Any) -> None:
        """Writes the preserved matched chunk directly into the `.tmp` atomic stream."""
        pass


class FilterEngine(ABC):
    """Processes parsed chunks through configurable constraint logic."""
    pass


class FileProcessor(ABC):
    """
    Main Orchestrator tying the Reader, Filter, Writer and Integrity mechanisms natively.
    """
    @abstractmethod
    def process(self) -> Dict[str, Any]:
        """
        Executes the file lifecycle cleanly returning localized stats block.
        """
        pass
