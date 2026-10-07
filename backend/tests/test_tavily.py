import pytest
from app.search.tavily_client import TavilySearchClient
from tavily import MissingAPIKeyError

def test_tavily_missing_key(monkeypatch):
    monkeypatch.setattr("app.config.settings.tavily_api_key", "")
    
    with pytest.raises(ValueError, match="Tavily API key is not configured properly"):
        client = TavilySearchClient()
        client.search("test query")

def test_tavily_search_success(monkeypatch, mocker):
    monkeypatch.setattr("app.config.settings.tavily_api_key", "test_key")
    
    mock_tavily_response = {
        "results": [
            {
                "title": "Test Title",
                "url": "http://test.com",
                "content": "Test content",
                "score": 0.99,
                "published_date": "2023-01-01",
                "source": "test.com"
            }
        ]
    }
    
    # Mock the underlying tavily.TavilyClient
    mock_client = mocker.Mock()
    mock_client.search.return_value = mock_tavily_response
    
    mocker.patch("app.search.tavily_client.TavilyClient", return_value=mock_client)
    
    client = TavilySearchClient()
    results = client.search("test query")
    
    assert len(results) == 1
    assert results[0].title == "Test Title"
    assert results[0].url == "http://test.com"
    assert results[0].content == "Test content"
    assert results[0].score == 0.99
    assert results[0].source == "test.com"
    assert results[0].retrieved_at is not None
