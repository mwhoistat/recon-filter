"""
Advanced Filtering Engine replacing old functionality with Security Hardened protections.
"""
import re
import time
from typing import Tuple, Optional
from recon_filter.config import FilterConfig

class RuleCompiler:
    """Safely compiles execution boundaries with Regex DoS protection bounds natively."""
    
    @staticmethod
    def compile_regex(pattern: Optional[str], case_sensitive: bool, safe_mode: bool) -> Optional[re.Pattern]:
        if not pattern:
            return None
            
        if safe_mode:
            # Simple heuristic regex complexity limiter blocking catastrophic backtracking vectors
            if "(.*" in pattern or pattern.count('*') > 3 or pattern.count('+') > 3:
                raise ValueError("Regex pattern violates Safe Mode complexity heuristics. Too many quantifiers.")
                
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.compile(pattern, flags=flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}")


def apply_filters(
    line: str, 
    config: FilterConfig, 
    compiled_regex: Optional[re.Pattern] = None,
    deadline: Optional[float] = None
) -> Tuple[bool, int]:
    """
    Applies the configured advanced enterprise filters to a string chunk.
    Enforces Negative Filtering, Thresholds, and Timeout bounds dynamically.
    """
    # 0. Timeout Bound Execution
    if deadline and time.time() > deadline:
        raise TimeoutError("Execution exceeded configured timeout bound limits.")

    original_line = line
    
    # 1. Negative Filtering (Immediate Rejection)
    if config.exclude_keywords:
        target_eval = original_line if config.case_sensitive else original_line.lower()
        for neg_kw in config.exclude_keywords:
            kw_eval = neg_kw if config.case_sensitive else neg_kw.lower()
            if kw_eval in target_eval:
                return False, 0
                
    # 2. Length Validations (Fast abort)
    if config.min_length > 0 and len(original_line) < config.min_length:
        return False, 0
    if config.max_length is not None and len(original_line) > config.max_length:
        return False, 0

    target_line = original_line if config.case_sensitive else original_line.lower()
    
    score = 0
    matches_regex = False
    
    # 3. Regex Processing
    if compiled_regex:
        if compiled_regex.search(original_line):
            matches_regex = True
            
    # 4. Keyword Processing & Scoring
    matches_keyword = False
    if config.keywords:
        if config.match_logic == "and":
            matches_keyword = True
            for kw in config.keywords:
                kw_target = kw if config.case_sensitive else kw.lower()
                if kw_target in target_line:
                    score += config.keyword_scores.get(kw, 0)
                else:
                    matches_keyword = False
                    break
        else:
            # OR Logic
            for kw in config.keywords:
                kw_target = kw if config.case_sensitive else kw.lower()
                if kw_target in target_line:
                    matches_keyword = True
                    score += config.keyword_scores.get(kw, 0)

    # 5. Auto Detection Defaults (If user specified NEITHER regex nor keywords, everything matches vacuously unless negative failed)
    if not config.keywords and not config.regex_pattern:
        return score >= config.min_score, score

    is_match = False
    has_regex = bool(config.regex_pattern)
    has_keywords = bool(config.keywords)

    if config.match_logic == "and":
        if has_regex and has_keywords:
            is_match = matches_regex and matches_keyword
        elif has_regex:
            is_match = matches_regex
        elif has_keywords:
            is_match = matches_keyword
    else:
        is_match = matches_regex or matches_keyword

    # 6. Score Threshold Filter
    if is_match and config.min_score > 0 and score < config.min_score:
        is_match = False

    return is_match, score
