"""
Unit tests for the core filtering and matching logic in recon-filter.
"""
import pytest
import re
from recon_filter.config import FilterConfig
from recon_filter.engine.filtering import RuleCompiler, apply_filters


def compile_regex(pattern, case_sensitive):
    """Compat wrapper for tests."""
    return RuleCompiler.compile_regex(pattern, case_sensitive, False)


def test_compile_regex_valid():
    compiled = compile_regex("^ERROR", False)
    assert isinstance(compiled, re.Pattern)

def test_compile_regex_invalid():
    with pytest.raises(ValueError):
        compile_regex("[invalid(regex", False)

def test_compile_regex_empty():
    assert compile_regex("", False) is None
    assert compile_regex(None, False) is None

def test_apply_filters_regex_match():
    config = FilterConfig(regex_pattern="fail", case_sensitive=False)
    compiled = compile_regex(config.regex_pattern, config.case_sensitive)
    
    is_match, score = apply_filters("this will fail", config, compiled)
    assert is_match is True
    
    is_match, score = apply_filters("this will PASS", config, compiled)
    assert is_match is False

def test_apply_filters_keywords_or_logic():
    config = FilterConfig(
        keywords=["apple", "banana"], 
        match_logic="or", 
        case_sensitive=False
    )
    
    # Matches one keyword
    is_match, _ = apply_filters("I like apple pie", config, None)
    assert is_match is True

    # Matches none
    is_match, _ = apply_filters("I like cherry pie", config, None)
    assert is_match is False

def test_apply_filters_keywords_and_logic():
    config = FilterConfig(
        keywords=["apple", "pie"], 
        match_logic="and", 
        case_sensitive=False
    )
    
    # Matches both keywords
    is_match, _ = apply_filters("I like apple pie", config, None)
    assert is_match is True

    # Matches only one keyword
    is_match, _ = apply_filters("I like apple juice", config, None)
    assert is_match is False

def test_apply_filters_case_sensitivity():
    config = FilterConfig(
        keywords=["Apple"], 
        case_sensitive=True
    )
    
    # Exact case matches
    is_match, _ = apply_filters("I eat an Apple", config, None)
    assert is_match is True

    # Incorrect case fails
    is_match, _ = apply_filters("I eat an apple", config, None)
    assert is_match is False

def test_apply_filters_length_constraints():
    config = FilterConfig(min_length=10, max_length=20)
    
    # Too short
    is_match, _ = apply_filters("short", config, None)
    assert is_match is False
    
    # Too long
    is_match, _ = apply_filters("this string is way too long for the filter requirement", config, None)
    assert is_match is False
    
    # Just right (vacuously true since no other regex/keywords are set)
    is_match, _ = apply_filters("perfect length", config, None)
    assert is_match is True

def test_apply_filters_combined_and():
    # Both Regex and Keywords MUST match
    config = FilterConfig(
        regex_pattern="^ERROR",
        keywords=["database"],
        match_logic="and",
        case_sensitive=False
    )
    compiled = compile_regex(config.regex_pattern, config.case_sensitive)
    
    # Matches both
    is_match, _ = apply_filters("ERROR: database connection lost", config, compiled)
    assert is_match is True

    # Matches regex, but missing keyword
    is_match, _ = apply_filters("ERROR: network timeout", config, compiled)
    assert is_match is False
    
    # Matches keyword, but misses regex anchor
    is_match, _ = apply_filters("WARN: database lagging", config, compiled)
    assert is_match is False
