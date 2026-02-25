"""
Intelligence Engine v2 — Risk-based scoring, endpoint heuristics,
fuzzy matching, and automatic threat tagging for reconnaissance data.
"""
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

# ------------------------------------------------------------------ #
#  Risk Weight Tables
# ------------------------------------------------------------------ #

KEYWORD_WEIGHTS: Dict[str, int] = {
    "apikey": 10, "api_key": 10, "secret": 10, "credential": 10,
    "password": 9, "passwd": 9, "token": 9, "access_token": 9,
    "auth": 8, "authorization": 8, "admin": 8, "login": 8,
    "private": 7, "internal": 7, "backup": 7, "config": 7,
    "database": 6, "db": 6, "endpoint": 6, "callback": 6,
    "debug": 5, "dev": 5, "staging": 5, "redirect": 5,
    "api": 3, "key": 3,
}

EXTENSION_RISK: Dict[str, int] = {
    ".env": 10, ".pem": 10, ".key": 10,
    ".sql": 9, ".bak": 9, ".old": 9, ".dump": 9,
    ".config": 8, ".cfg": 8, ".ini": 8, ".yml": 7, ".yaml": 7,
    ".php": 7, ".asp": 7, ".aspx": 7, ".jsp": 7,
    ".json": 5, ".xml": 5, ".log": 4,
    ".js": 3, ".css": 2, ".html": 2, ".txt": 1, ".md": 1,
}

PARAM_SENSITIVITY: Dict[str, int] = {
    "password": 10, "passwd": 10, "secret": 10, "token": 9,
    "api_key": 9, "apikey": 9, "key": 8, "auth": 8,
    "redirect": 7, "redirect_uri": 7, "callback": 7, "return_url": 7,
    "next": 6, "url": 6, "file": 6, "path": 6,
    "cmd": 8, "exec": 8, "query": 5, "search": 4,
    "id": 3, "page": 2, "sort": 1, "limit": 1,
}

ADMIN_PATTERNS = ["/admin", "/wp-admin", "/administrator", "/manager", "/dashboard", "/panel", "/cpanel", "/phpmyadmin"]
API_PATTERNS = ["/api/", "/v1/", "/v2/", "/v3/", "/graphql", "/rest/", "/rpc/", "/oauth"]
BACKUP_EXTENSIONS = [".bak", ".old", ".sql", ".dump", ".gz", ".tar", ".zip", ".sql.gz", ".backup"]
DEV_PATTERNS = ["/staging", "/dev", "/test", "/debug", "/beta", "/sandbox", "/internal"]

# ------------------------------------------------------------------ #
#  Risk Tags
# ------------------------------------------------------------------ #

def risk_tag(score: int) -> str:
    """Return a risk label based on score thresholds."""
    if score >= 15:
        return "[HIGH]"
    elif score >= 8:
        return "[MEDIUM]"
    return "[LOW]"


# ------------------------------------------------------------------ #
#  Intelligence Engine
# ------------------------------------------------------------------ #

class IntelligenceEngine:
    """
    Risk-based intelligence engine combining keyword scoring, fuzzy matching,
    URL structure analysis, extension risk, parameter sensitivity,
    and endpoint heuristics into a unified scoring pipeline.
    """

    def __init__(
        self,
        priority_keywords: Optional[List[str]] = None,
        fuzzy_threshold: float = 0.75,
        risk_threshold: int = 0,
    ):
        self.fuzzy_threshold = fuzzy_threshold
        self.risk_threshold = risk_threshold

        self.weights: Dict[str, int] = dict(KEYWORD_WEIGHTS)
        if priority_keywords:
            for kw in priority_keywords:
                self.weights[kw.lower()] = max(self.weights.get(kw.lower(), 0), 10)

    # ------------------------------------------------------------------ #
    #  Main Scoring Pipeline
    # ------------------------------------------------------------------ #

    def analyze(self, line: str, keywords: List[str]) -> Tuple[int, str, str, List[str]]:
        """
        Full intelligence analysis on a single line.
        Returns: (score, risk_tag, classification, matched_keywords)
        """
        score = 0
        matched: List[str] = []

        # 1. Keyword scoring (exact + fuzzy)
        kw_score, kw_matched = self._keyword_score(line, keywords)
        score += kw_score
        matched.extend(kw_matched)

        # 2. URL / extension / parameter analysis
        classification = self._classify(line)
        score += self._structural_score(line, classification)

        # 3. Endpoint heuristics
        score += self._heuristic_score(line)

        tag = risk_tag(score)
        return score, tag, classification, matched

    def passes_threshold(self, score: int) -> bool:
        """Check if a score meets the configured risk threshold."""
        return score >= self.risk_threshold

    # ------------------------------------------------------------------ #
    #  Keyword Scoring
    # ------------------------------------------------------------------ #

    def _keyword_score(self, line: str, keywords: List[str]) -> Tuple[int, List[str]]:
        line_lower = line.lower()
        total = 0
        matched: List[str] = []

        for kw in keywords:
            kw_lower = kw.lower()
            weight = self.weights.get(kw_lower, 1)

            if kw_lower in line_lower:
                total += weight
                matched.append(kw)
            elif self._fuzzy_match(kw_lower, line_lower):
                total += max(1, int(weight * 0.6))
                matched.append(f"{kw}~")

        return total, matched

    def _fuzzy_match(self, keyword: str, text: str) -> bool:
        tokens = text.replace("/", " ").replace("?", " ").replace("&", " ").replace("=", " ").split()
        for token in tokens:
            if len(token) < 2:
                continue
            if SequenceMatcher(None, keyword, token).ratio() >= self.fuzzy_threshold:
                return True
        return False

    # ------------------------------------------------------------------ #
    #  Classification
    # ------------------------------------------------------------------ #

    @staticmethod
    def _classify(line: str) -> str:
        s = line.strip()
        if "://" in s or s.startswith("www."):
            return "url"
        if s.startswith("/") and not s.startswith("//"):
            return "path"
        if "=" in s and ("&" in s or "?" in s):
            return "parameter"
        return "generic"

    # ------------------------------------------------------------------ #
    #  Structural Scoring
    # ------------------------------------------------------------------ #

    def _structural_score(self, line: str, classification: str) -> int:
        score = 0
        stripped = line.strip()

        if classification == "url":
            try:
                target = stripped if "://" in stripped else f"http://{stripped}"
                parsed = urlparse(target)

                # Extension risk
                path = parsed.path or ""
                if "." in path.split("/")[-1]:
                    ext = "." + path.split("/")[-1].rsplit(".", 1)[-1].lower()
                    score += EXTENSION_RISK.get(ext, 0)

                # Parameter sensitivity
                if parsed.query:
                    params = parse_qs(parsed.query)
                    for pname in params:
                        score += PARAM_SENSITIVITY.get(pname.lower(), 1)

                # Path depth bonus
                depth = len([p for p in path.split("/") if p])
                score += min(depth, 4)

            except Exception:
                pass

        elif classification == "path":
            parts = [p for p in stripped.split("/") if p]
            score += min(len(parts), 3)

            if "." in parts[-1] if parts else False:
                ext = "." + parts[-1].rsplit(".", 1)[-1].lower()
                score += EXTENSION_RISK.get(ext, 0)

        return score

    # ------------------------------------------------------------------ #
    #  Endpoint Heuristics
    # ------------------------------------------------------------------ #

    @staticmethod
    def _heuristic_score(line: str) -> int:
        lower = line.lower()
        score = 0

        for pattern in ADMIN_PATTERNS:
            if pattern in lower:
                score += 6
                break

        for pattern in API_PATTERNS:
            if pattern in lower:
                score += 4
                break

        for ext in BACKUP_EXTENSIONS:
            if lower.endswith(ext):
                score += 5
                break

        for pattern in DEV_PATTERNS:
            if pattern in lower:
                score += 3
                break

        return score

    # ------------------------------------------------------------------ #
    #  Format Output
    # ------------------------------------------------------------------ #

    @staticmethod
    def format_tagged(line: str, score: int, tag: str) -> str:
        """Format a line with its risk tag and score for output."""
        return f"{tag} [score:{score}] {line.rstrip()}"
