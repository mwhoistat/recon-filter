import pytest
import os
import json
import csv
from pathlib import Path
from recon_filter.config import FilterConfig
from recon_filter.engine.core import EngineProcessor
from recon_filter.security.integrity import calculate_sha256

def test_json_preservation(tmp_path):
    json_path = tmp_path / "test.json"
    
    # Valid structure input
    data = [{"id": 1, "msg": "CRITICAL error"}, {"id": 2, "msg": "INFO okay"}]
    with open(json_path, 'w') as f:
        json.dump(data, f)
        
    config = FilterConfig(
        regex_pattern="CRITICAL",
        generate_hash_report=True
    )
    
    processor = EngineProcessor(json_path, tmp_path, config)
    stats = processor.process()
    
    assert stats["matches_found"] == 1
    
    out_file = tmp_path / "test_filtered.json"
    assert out_file.exists()
    
    with open(out_file, 'r') as f:
        res = json.load(f)
        assert len(res) == 1
        assert "CRITICAL" in res[0]["msg"]
        
    assert stats["hash_post"] != "disabled"

def test_csv_preservation(tmp_path):
    csv_path = tmp_path / "test.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "msg"])
        writer.writerow(["1", "FATAL crash"])
        writer.writerow(["2", "debug trace"])
        
    config = FilterConfig(
        regex_pattern="FATAL"
    )
    
    processor = EngineProcessor(csv_path, tmp_path, config)
    processor.process()
    
    out_file = tmp_path / "test_filtered.csv"
    
    with open(out_file, 'r', newline='') as f:
        reader = list(csv.reader(f))
        assert len(reader) == 2 # header + 1 match
        assert reader[0] == ["id", "msg"]
        assert "FATAL" in reader[1][1]

def test_backup_system(tmp_path):
    txt_path = tmp_path / "test.txt"
    with open(txt_path, 'w') as f:
        f.write("line 1\nline 2\n")
        
    config = FilterConfig(
        keywords=["line"],
        no_backup=False
    )
    
    processor = EngineProcessor(txt_path, tmp_path, config)
    processor.process()
    
    bak_file = tmp_path / "test.txt.bak"
    assert bak_file.exists()
    
def test_preview_mode(tmp_path):
    txt_path = tmp_path / "test.txt"
    with open(txt_path, 'w') as f:
        f.write("match_1\nmatch_2\nmiss_1\n")
        
    config = FilterConfig(
        regex_pattern="match",
        preview=True
    )
    
    processor = EngineProcessor(txt_path, tmp_path, config)
    stats = processor.process()
    
    # Assert preview buffer returned data
    assert stats["matches_found"] == 2
    assert "match_1\n" in stats["preview_buffer"] or "match_1" in stats["preview_buffer"]
    
    # Assert physical write did NOT happen
    out_file = tmp_path / "test_filtered.txt"
    assert not out_file.exists()
