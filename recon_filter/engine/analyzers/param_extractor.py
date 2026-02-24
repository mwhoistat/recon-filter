"""
Extrapolates and tracks URL Parameters mapping a static O(1) Counter dynamically.
"""
import json
from collections import Counter
from urllib.parse import urlparse, parse_qs
from pathlib import Path

class ParameterExtractor:
    """Manages lightweight parameter extraction generating output constraints cleanly."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir if output_dir else Path(".")
        self.param_counter = Counter()
        self.total_urls_processed = 0

    def extract(self, url: str) -> None:
        """
        Extracts parameters mapping them mathematically to the Counter securely.
        Never holds entire URLs or arrays natively.
        """
        self.total_urls_processed += 1
        try:
            parsed = urlparse(url.strip())
            if parsed.query:
                params = parse_qs(parsed.query, keep_blank_values=True)
                for param in params.keys():
                    self.param_counter[param] += 1
        except ValueError:
            pass

    def generate_report(self) -> None:
        """Dumps internal O(1) structural stats locally upon execution hook limits."""
        if not self.param_counter:
            return

        report_path = self.output_dir / "parameter_summary.json"
        
        most_common = self.param_counter.most_common(10)
        
        payload = {
            "total_urls_analyzed_for_params": self.total_urls_processed,
            "total_unique_parameters": len(self.param_counter),
            "top_10_most_frequent_parameters": [{"parameter": k, "frequency": v} for k, v in most_common],
            "complete_frequency_distribution": dict(self.param_counter)
        }
        
        try:
            with report_path.open('w', encoding='utf-8') as f:
                json.dump(payload, f, indent=4)
        except Exception:
            pass
