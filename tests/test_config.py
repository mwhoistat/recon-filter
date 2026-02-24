"""
Additional unit tests for v2 features in recon-filter.
"""
import pytest
import os
from pathlib import Path
from recon_filter.config import ConfigManager, FilterConfig

def test_config_generation_and_loading(tmp_path):
    # Test YAML creation
    yaml_path = tmp_path / "test_config.yaml"
    ConfigManager.generate_default(yaml_path)
    
    assert yaml_path.exists()
    
    # Test parsing back
    loaded = ConfigManager.load(yaml_path)
    assert loaded.match_logic == "or"
    assert loaded.regex_pattern == "^CRITICAL|^ERROR"

def test_config_json_format(tmp_path):
    json_path = tmp_path / "test_config.json"
    
    config = FilterConfig(
        keywords=["test1", "test2"],
        match_limit=50,
        dry_run=True
    )
    
    ConfigManager.save(config, json_path)
    assert json_path.exists()
    
    loaded = ConfigManager.load(json_path)
    assert loaded.keywords == ["test1", "test2"]
    assert loaded.match_limit == 50
    assert loaded.dry_run is True

def test_config_invalid_extension(tmp_path):
    bad_path = tmp_path / "test.txt"
    with pytest.raises(ValueError):
        ConfigManager.save(FilterConfig(), bad_path)
