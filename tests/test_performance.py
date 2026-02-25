import pytest
import tempfile
import json
from pathlib import Path

from recon_filter.config import FilterConfig
from recon_filter.engine.core import EngineProcessor
from recon_filter.engine.cache import CacheManager
from recon_filter.security.integrity import calculate_sha256

def test_cache_bypassing(tmp_path):
    # Setup test file
    test_file = tmp_path / "cache_test.txt"
    with test_file.open('w') as f:
        f.write("error map 1\nerror map 2\n")
        
    config = FilterConfig(
        regex_pattern="error",
    )
    
    # Run 1: Should process and cache
    processor = EngineProcessor(test_file, tmp_path, config)
    stats1 = processor.process()
    
    assert stats1["matches_found"] == 2
    assert stats1["skipped_cache"] is False
    
    # Run 2: Should hit cache
    processor2 = EngineProcessor(test_file, tmp_path, config)
    stats2 = processor2.process()
    
    assert stats2["skipped_cache"] is True
    assert stats2["matches_found"] == 0 # Bypassed entirely
    assert stats2["duration_seconds"] == 0.0
    
def test_ijson_streaming_preservation(tmp_path):
    json_path = tmp_path / "huge_mock.json"
    
    # Mocking a list of dicts directly
    data = [{"id": i, "val": "CRITICAL" if i % 2 == 0 else "INFO"} for i in range(10)]
    with json_path.open('w') as f:
        json.dump(data, f)
        
    config = FilterConfig(
        regex_pattern="CRITICAL"
    )
    
    processor = EngineProcessor(json_path, tmp_path, config)
    stats = processor.process()
    
    assert stats["matches_found"] == 5
    
    out_file = tmp_path / "huge_mock_filtered.json"
    assert out_file.exists()
    
    with out_file.open('r') as f:
        rendered = json.load(f)
        assert len(rendered) == 5
        assert all("CRITICAL" in r["val"] for r in rendered)
