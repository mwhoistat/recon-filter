"""
Smart Filtering Engine providing context-aware scoring, fuzzy matching,
and priority keyword weighting for intelligent reconnaissance filtering.
"""
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs


# Default priority weights for common reconnaissance keywords
DEFAULT_PRIORITY_WEIGHTS: Dict[str, int] = {
    "apikey": 10, "api_key": 10, "secret": 9, "credential": 9,
    "password": 8, "passwd": 8, "token": 8, "access_token": 8,
    "auth": 7, "authorization": 7, "admin": 7, "login": 7,
    "config": 6, "backup": 6, "private": 6, "internal": 6,
    "database": 5, "db": 5, "endpoint": 5, "callback": 5,
    "debug": 4, "dev": 4, "staging": 4, "redirect": 4,
    "api": 3, "key": 3,
}


class SmartScorer:
    """
    Context-aware scoring engine applying weighted keyword analysis,
    fuzzy matching, and URL structure recognition to each processed line.
    """

    def __init__(
        self,
        priority_keywords: Optional[List[str]] = None,
        fuzzy_threshold: float = 0.75,
        custom_weights: Optional[Dict[str, int]] = None,
    ):
        self.fuzzy_threshold = fuzzy_threshold

        # Build weight map: defaults + custom overrides + priority boosts
        self.weights: Dict[str, int] = dict(DEFAULT_PRIORITY_WEIGHTS)
        if custom_weights:
            self.weights.update(custom_weights)

        # Priority keywords get maximum weight if not already higher
        if priority_keywords:
            for kw in priority_keywords:
                kw_lower = kw.lower()
                self.weights[kw_lower] = max(self.weights.get(kw_lower, 0), 10)

    # ------------------------------------------------------------------ #
    #  Core Scoring
    # ------------------------------------------------------------------ #

    def score_line(self, line: str, keywords: List[str]) -> Tuple[int, List[str]]:
        """
        Score a line against keywords using exact + fuzzy matching.
        Returns (total_score, list_of_matched_keywords).
        """
        line_lower = line.lower()
        total_score = 0
        matched: List[str] = []

        for kw in keywords:
            kw_lower = kw.lower()
            weight = self.weights.get(kw_lower, 1)

            # Exact match
            if kw_lower in line_lower:
                total_score += weight
                matched.append(kw)
                continue

            # Fuzzy match against tokens in the line
            if self._fuzzy_match(kw_lower, line_lower):
                # Fuzzy hits score at 60% of the exact weight
                total_score += max(1, int(weight * 0.6))
                matched.append(f"{kw}~")

        # Structural bonus: URL with query params gets +2
        if "://" in line or line.startswith("www."):
            total_score += self._url_structure_bonus(line)

        return total_score, matched

    def _fuzzy_match(self, keyword: str, text: str) -> bool:
        """Token-level fuzzy matching using SequenceMatcher."""
        tokens = text.replace("/", " ").replace("?", " ").replace("&", " ").replace("=", " ").split()
        for token in tokens:
            if len(token) < 2:
                continue
            ratio = SequenceMatcher(None, keyword, token).ratio()
            if ratio >= self.fuzzy_threshold:
                return True
        return False

    @staticmethod
    def _url_structure_bonus(line: str) -> int:
        """Awards bonus points based on URL structural complexity."""
        bonus = 0
        try:
            target = line.strip()
            if "://" not in target:
                target = f"http://{target}"
            parsed = urlparse(target)
            if parsed.query:
                params = parse_qs(parsed.query)
                # More params = higher value target
                bonus += min(len(params), 5)
            if parsed.path and parsed.path != "/":
                bonus += 1
        except Exception:
            pass
        return bonus

    # ------------------------------------------------------------------ #
    #  Chain Filtering Pipeline
    # ------------------------------------------------------------------ #

    @staticmethod
    def classify_line(line: str) -> str:
        """
        Classify a line into a content category for chain filtering.
        Returns: 'url', 'path', 'parameter', 'keyword_hit', or 'generic'.
        """
        stripped = line.strip()

        # URL detection
        if "://" in stripped or stripped.startswith("www."):
            return "url"

        # File path detection (Unix-style)
        if stripped.startswith("/") and not stripped.startswith("//"):
            return "path"

        # Query parameter detection
        if "=" in stripped and ("&" in stripped or "?" in stripped):
            return "parameter"

        return "generic"

    def chain_filter(
        self,
        line: str,
        keywords: List[str],
        stages: Optional[List[str]] = None,
    ) -> Tuple[bool, int, str]:
        """
        Multi-layer chain filter: keyword → URL → parameter → path cluster.
        Returns (passed, score, classification).
        """
        if stages is None:
            stages = ["keyword", "url", "parameter", "path"]

        classification = self.classify_line(line)
        score, matched = self.score_line(line, keywords)

        # Stage 1: Keyword match required
        if "keyword" in stages and not matched:
            return False, 0, classification

        # Stage 2: URL structure validation
        if "url" in stages and classification == "url":
            score += 2  # URL lines get a relevance bump

        # Stage 3: Parameter extraction bonus
        if "parameter" in stages and classification in ("url", "parameter"):
            if "=" in line:
                score += 1

        # Stage 4: Path clustering bonus
        if "path" in stages and classification == "path":
            score += 1

        return score > 0, score, classification
