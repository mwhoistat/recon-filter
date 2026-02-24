"""
URL Analytics Engine executing robust parsing natively maintaining streaming limits securely.
"""
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs
import collections

class UrlAnalyzer:
    """
    Stateless high-performance URL parser validating structural domains natively.
    """
    
    def __init__(self, config):
        self.config = config
        # We hold lightweight metrics internally, flushing logic securely handled upstream
        self.param_metrics = collections.defaultdict(int) 

    def analyze_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Takes an arbitrary line or string token. 
        Returns (is_valid_url, fixed_url_string).
        """
        # If strict URL is off and it's not a URL, we simply pass it through as valid raw data.
        original_token = token.strip()
        parsing_target = original_token
        
        # Heuristics for "looks like a URL"
        looks_like_url = "://" in parsing_target or parsing_target.startswith("www.") or (
           "/" in parsing_target and "." in parsing_target.split("/")[0]
        )
        
        if not looks_like_url:
             if self.config.strict_url:
                 return False, None
             return True, original_token

        if self.config.allow_no_scheme and "://" not in parsing_target:
            parsing_target = f"http://{parsing_target}"

        try:
            parsed = urlparse(parsing_target)
            
            # A completely valid domain structurally requires a netloc and scheme
            is_valid = bool(parsed.scheme and parsed.netloc)
            
            if is_valid:
                # Execution bindings for Extraction
                if self.config.extract_params or self.config.param_report:
                    self._extract_parameters(parsed, parsing_target)
                
                return True, parsing_target
                
        except Exception:
            pass # Parsing failure
            
        if self.config.strict_url:
            return False, None
            
        return True, original_token

    def _extract_parameters(self, parsed_url, original_url: str):
        """Builds statistical mapping of observed GET endpoints cleanly natively."""
        if not parsed_url.query:
            return
            
        params = parse_qs(parsed_url.query)
        for param_name, values in params.items():
            # We specifically key by the param_name across all endpoints uniquely as requested
            key = f"{param_name}"
            # O(1) Counting hash
            self.param_metrics[key] += len(values)

    def extract_extension(self, token: str) -> str:
        """Determines the active extension (.php, .json) or returns 'none'."""
        try:
            target = token if "://" in token else f"http://{token}"
            parsed = urlparse(target)
            path = parsed.path
            
            if "." in path.split("/")[-1]:
                ext = path.split("/")[-1].split(".")[-1]
                if ext.isalnum():
                    return f".{ext.lower()}"
        except Exception:
            pass
            
        return "none"
        
    def extract_depth(self, token: str) -> int:
        """Counts the URL directory boundaries natively."""
        try:
            target = token if "://" in token else f"http://{token}"
            parsed = urlparse(target)
            path = parsed.path
            parts = [p for p in path.split("/") if p]
            
            depth = len(parts)
            if self.config.depth_limit is not None:
                depth = min(depth, self.config.depth_limit)
            return depth
        except Exception:
            pass
        return 0

    def generate_report(self) -> Dict[str, Any]:
        """Returns the fully parsed parameter distributions as a dictionary."""
        report = []
        for param, count in self.param_metrics.items():
            report.append({
                "parameter_name": param,
                "detected_count": count
            })
        return {"parameters": report}
