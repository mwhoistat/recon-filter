import json
import pytest
import shutil
from pathlib import Path

from recon_filter.config import FilterConfig
from recon_filter.engine.core import EngineProcessor
from recon_filter.engine.analyzers.url_processor import URLProcessor
from recon_filter.engine.analyzers.param_extractor import ParameterExtractor
from recon_filter.engine.analyzers.cluster_engine import ClusterEngine

def test_url_processor_validation():
    # Valid
    assert URLProcessor.looks_like_url("https://example.com") is True
    assert URLProcessor.is_valid_url("https://example.com/api/v1?user=admin") is True
    assert URLProcessor.is_valid_url("http://127.0.0.1:8080/admin") is True
    
    # Invalid
    assert URLProcessor.is_valid_url("https://invalid path") is False
    assert URLProcessor.looks_like_url("just a string") is False

def test_param_extractor(tmp_path):
    extractor = ParameterExtractor(tmp_path)
    
    urls = [
        "https://test.com?id=1&role=admin",
        "https://test.com?id=2",
        "https://test.com?token=xyz",
        "https://invalid.com/no_params"
    ]
    
    for url in urls:
        extractor.extract(url)
        
    assert extractor.total_urls_processed == 4
    assert extractor.param_counter["id"] == 2
    assert extractor.param_counter["role"] == 1
    assert extractor.param_counter["token"] == 1

def test_cluster_engine(tmp_path):
    cluster = ClusterEngine(tmp_path, enable_extension=True, enable_depth=True)
    
    paths = [
        "https://test.com/assets/app.js",
        "/var/www/html/index.html",
        "https://test.com/api/users",
        "/a/b/c/d"
    ]
    
    for p in paths:
        cluster.process(p)
        
    # Check stats
    assert cluster.total_clustered == 4
    assert cluster.depth_counter["depth_2"] == 2
    assert cluster.depth_counter["depth_4"] == 2
    
    js_dir = tmp_path / "js"
    html_dir = tmp_path / "html"
    no_ext_dir = tmp_path / "no_extension"
    
    assert js_dir.exists()
    assert html_dir.exists()
    assert no_ext_dir.exists()
    
    # js contents
    content = (js_dir / "cluster.txt").read_text()
    assert "app.js" in content

def test_engine_integration(tmp_path):
    src = tmp_path / "test_urls.txt"
    src.write_text("https://example.com/app.js?id=1\nhttps://example.com/logo.png?id=2\n")
    
    config = FilterConfig(
        regex_pattern="https://",
        url_mode=True,
        extract_params=True,
        cluster_extension=True,
        no_backup=True
    )
    
    processor = EngineProcessor(src, tmp_path, config)
    stats = processor.process()
    
    assert stats["matches_found"] == 2
    assert stats["param_stats"]["id"] == 2
    
    js_dir = tmp_path / "js"
    assert js_dir.exists()
