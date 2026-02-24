"""
JSON format preservation utilizing iterative JSON parsing (`ijson`) yielding extreme memory efficiency.
"""
import json
import ijson
from pathlib import Path
from typing import Iterator, Any

from recon_filter.config import FilterConfig
from recon_filter.engine.interfaces import FileReader, OutputWriter

class JsonFileReader(FileReader):
    def __init__(self, filepath: Path, config: FilterConfig):
        super().__init__(filepath, config)
        
    def read(self) -> Iterator[Any]:
        # Employs `ijson.items` to iteratively parse large JSON arrays/dicts yielding structures
        # lazily rather than loading multi-GB objects into RAM.
        with self.filepath.open('rb') as f:
            try:
                # First, infer if it's an array or top-level dictionary
                parser = ijson.parse(f)
                prefix_type = None
                for prefix, event, value in parser:
                    if event == 'start_array':
                        prefix_type = 'array'
                        break
                    elif event == 'start_map':
                        prefix_type = 'map'
                        break
                        
                f.seek(0)
                        
                if prefix_type == 'array':
                    # Parse each array object natively
                    objects = ijson.items(f, 'item')
                    for obj in objects:
                        yield json.dumps(obj)
                else:
                    # Treat root maps by iteratively parsing top-level string keys natively
                    kv_pairs = ijson.kvitems(f, '')
                    for k, v in kv_pairs:
                        yield json.dumps({k: v})

            except (ijson.JSONError, ValueError) as e:
                raise ValueError(f"JSON Iterative validation failed on {self.filepath.name}: {e}")


class JsonOutputWriter(OutputWriter):
    def __init__(self, filepath: Path, config: FilterConfig):
        super().__init__(filepath, config)
        self.file = None
        self.first_item = True
        
    def __enter__(self):
        if not self.config.dry_run and not self.config.preview:
            # Atomic Target is used
            self.file = open(self.atomic_path, 'w', encoding=self.config.encoding or 'utf-8')
            if not self.config.append_mode:
                self.file.write("[\n")
        return self
        
    def _close_file(self):
        if self.file:
            if not self.config.append_mode:
                self.file.write("\n]\n")
            self.file.close()
            self.success = True
            
    def write(self, item: str) -> None:
        if self.file:
            prefix = "  " if self.first_item else ",\n  "
            try:
                valid_struct = json.loads(item)
                self.file.write(f'{prefix}{json.dumps(valid_struct, indent=None)}')
            except json.JSONDecodeError:
                self.file.write(f'{prefix}{json.dumps(item)}')
                
            self.first_item = False
