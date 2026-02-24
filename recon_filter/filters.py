"""
Core filtering logic for matching strings against keywords or regex patterns.
"""
import re
from typing import Tuple, Optional
from recon_filter.config import FilterConfig


def compile_regex(pattern: Optional[str], case_sensitive: bool) -> Optional[re.Pattern]:
    """
    Compiles a regex pattern safely for performance optimization during streaming.
    
    Args:
        pattern (Optional[str]): The regex pattern string.
        case_sensitive (bool): Flag indicating if matching should be case-sensitive.
        
    Raises:
        ValueError: If the regex pattern is invalid.
        
    Returns:
        Optional[re.Pattern]: Compiled regex pattern if valid, else None.
    """
    if not pattern:
        return None
    try:
        flags = 0 if case_sensitive else re.IGNORECASE
        return re.compile(pattern, flags=flags)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern '{pattern}': {e}")


def apply_filters(line: str, config: FilterConfig, compiled_regex: Optional[re.Pattern] = None) -> Tuple[bool, int]:
    """
    Applies the configured filters to a single line of text.
    
    Args:
        line (str): The raw line from the file.
        config (FilterConfig): User-defined filter configuration.
        compiled_regex (Optional[re.Pattern]): Pre-compiled regex pattern for fast regex eval.
        
    Returns:
        Tuple[bool, int]: (True if the line passes all filters, calculated score)
    """
    original_line = line
    
    # 1. Length Validations (Fast abort)
    if config.min_length > 0 and len(original_line) < config.min_length:
        return False, 0
    if config.max_length is not None and len(original_line) > config.max_length:
        return False, 0

    target_line = original_line if config.case_sensitive else original_line.lower()
    
    score = 0
    matches_regex = False
    
    # 2. Regex Processing
    if compiled_regex:
        # Match against `original_line` because compiled_regex has IGNORECASE built-in
        if compiled_regex.search(original_line):
            matches_regex = True
            
    # 3. Keyword Processing & Scoring
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
                    # Abort AND sequence early for performance
                    break
        else:
            # OR Logic
            for kw in config.keywords:
                kw_target = kw if config.case_sensitive else kw.lower()
                if kw_target in target_line:
                    matches_keyword = True
                    score += config.keyword_scores.get(kw, 0)

    # 4. Combinatorial Logic resolution
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
        # 'or' logic overrides
        is_match = matches_regex or matches_keyword

    # 5. Score Threshold Filter
    if is_match and config.min_score > 0 and score < config.min_score:
        is_match = False

    return is_match, score
