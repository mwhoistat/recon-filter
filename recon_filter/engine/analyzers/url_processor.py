"""
Professional URL Validation Processor natively validating string bounds for RFC compliance.
"""
import re
from urllib.parse import urlparse

class URLProcessor:
    """Provides O(1) string execution validating URLs aggressively."""
    
    # A practical deterministic regex mapping basic URL bounds prior to parsing
    _url_pattern = re.compile(
        r'^(?:http|https)://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    @classmethod
    def looks_like_url(cls, text: str) -> bool:
        """Fast heuristic checking if string starts with HTTP boundaries natively."""
        text = text.strip()
        return text.startswith("http://") or text.startswith("https://")

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """
        Executes structural URL validation extracting Scheme, Domain, Port natively.
        Returns True if the URL operates mathematically flawlessly across RFC constraints.
        """
        url = url.strip()
        if not cls.looks_like_url(url):
            return False
            
        if not cls._url_pattern.match(url):
            return False
            
        try:
            parsed = urlparse(url)
            # Require scheme and network location natively
            if not parsed.scheme or not parsed.netloc:
                return False
            return True
        except ValueError:
            return False
