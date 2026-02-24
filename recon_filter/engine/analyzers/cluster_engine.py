"""
Engine routing mappings into dynamically clustered directory structures efficiently natively.
"""
import os
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter

class ClusterEngine:
    """
    Manages structural mapping generating path bounds without blowing up File limits.
    """
    
    def __init__(self, output_dir: Path, enable_extension: bool = False, enable_depth: bool = False):
        self.output_dir = output_dir if output_dir else Path(".")
        self.enable_extension = enable_extension
        self.enable_depth = enable_depth
        
        self.file_handlers = {}
        
        # Depth Statistics mapped dynamically O(1)
        self.depth_counter = Counter()
        self.total_clustered = 0

    def _extract_path(self, text: str) -> str:
        """Deduces strictly the URL path natively without query scopes."""
        text = text.strip()
        if text.startswith("http://") or text.startswith("https://"):
            try:
                return urlparse(text).path
            except ValueError:
                return text
        return text

    def process(self, text: str) -> None:
        """
        Calculates cluster bounds routing the text directly into the mapped output files.
        """
        self.total_clustered += 1
        path_str = self._extract_path(text)
        
        if self.enable_extension:
            ext = self._get_extension(path_str)
            cluster_name = f"{ext}" if ext else "no_extension"
            target_dir = self.output_dir / cluster_name
            self._write_cluster_chunk(target_dir, "cluster.txt", text)

        if self.enable_depth:
            depth = self._get_depth(path_str)
            cluster_name = f"depth_{depth}"
            self.depth_counter[cluster_name] += 1
            target_dir = self.output_dir / cluster_name
            self._write_cluster_chunk(target_dir, "cluster.txt", text)

    def _get_extension(self, path: str) -> str:
        """Returns bounds stripped from the Path cleanly."""
        name = os.path.basename(path)
        if "." in name:
            ext = name.split(".")[-1].lower()
            if ext.isalnum() and len(ext) < 10:
                 return ext
        return ""

    def _get_depth(self, path: str) -> int:
        """Calculates strict path depth structurally natively."""
        parts = [p for p in path.split("/") if p]
        return len(parts)

    def _write_cluster_chunk(self, directory: Path, filename: str, data: str) -> None:
        """Appends efficiently. Maintaining all handles open is risky over >1000 exts, will atomic open/close fast bounds."""
        os.makedirs(directory, exist_ok=True)
        target = directory / filename
        
        # We enforce line endings strictly parsing bounds natively without caching massive lists globally
        try:
            with target.open('a', encoding='utf-8') as f:
                f.write(data)
                if not data.endswith('\n'):
                    f.write('\n')
        except IOError:
            pass

    def generate_report(self) -> None:
        """Generates statistical trace for the depth metrics securely."""
        if not self.enable_depth or not self.depth_counter:
            return
            
        report_path = self.output_dir / "depth_clustering_summary.txt"
        
        try:
            with report_path.open('w', encoding='utf-8') as f:
                f.write("Recon-Filter Depth Clustering Summary\n")
                f.write("="*40 + "\n")
                f.write(f"Total entries processed: {self.total_clustered}\n\n")
                
                most_common = self.depth_counter.most_common(1)
                if most_common:
                    f.write(f"Most common depth: {most_common[0][0]} ({most_common[0][1]} lines)\n\n")
                
                f.write("Depth Distribution:\n")
                for depth, count in self.depth_counter.most_common():
                     f.write(f"  - {depth}: {count} hits\n")
        except IOError:
            pass
