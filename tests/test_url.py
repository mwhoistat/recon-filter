import pytest
from recon_filter.config import FilterConfig
from recon_filter.engine.url_analyzer import UrlAnalyzer

def test_url_analyzer_strict_mode():
    config = FilterConfig(strict_url=True)
    analyzer = UrlAnalyzer(config)
    
    # Valid url
    is_valid, token = analyzer.analyze_token("https://example.com/api/v1?token=123")
    assert is_valid is True
    assert token == "https://example.com/api/v1?token=123"
    
    # Invalid url dropped
    is_valid, token = analyzer.analyze_token("just some random log string")
    assert is_valid is False
    assert token is None

def test_url_analyzer_allow_no_scheme():
    config = FilterConfig(allow_no_scheme=True, strict_url=True)
    analyzer = UrlAnalyzer(config)
    
    # Missing scheme natively fixed
    is_valid, token = analyzer.analyze_token("api.example.com/v1/auth")
    assert is_valid is True
    assert token == "http://api.example.com/v1/auth"
    
def test_url_analyzer_param_extraction():
    config = FilterConfig(extract_params=True)
    analyzer = UrlAnalyzer(config)
    
    analyzer.analyze_token("https://test.com/login?user=admin&id=5")
    analyzer.analyze_token("https://test.com/login?user=root")
    analyzer.analyze_token("https://test.com/login?user=guest&id=5")
    
    report = analyzer.generate_report()
    params = report["parameters"]
    
    user_param = next(p for p in params if p["parameter_name"] == "user")
    id_param = next(p for p in params if p["parameter_name"] == "id")
    
    assert user_param["detected_count"] == 3
    assert id_param["detected_count"] == 2

def test_url_analyzer_depth_extraction():
    config = FilterConfig()
    analyzer = UrlAnalyzer(config)
    
    assert analyzer.extract_depth("https://test.com/") == 0
    assert analyzer.extract_depth("https://test.com/api") == 1
    assert analyzer.extract_depth("https://test.com/api/v1/users") == 3
