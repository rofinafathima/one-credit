import pytest
import httpx
from app.search.factcheck_client import GoogleFactCheckClient

@pytest.mark.asyncio
async def test_factcheck_missing_key(monkeypatch):
    monkeypatch.setattr("app.config.settings.google_fact_check_api_key", "")
    
    with pytest.raises(ValueError, match="GOOGLE_FACT_CHECK_API_KEY is missing from configuration."):
        client = GoogleFactCheckClient()
        await client.search("test query")

@pytest.mark.asyncio
async def test_factcheck_search_success(monkeypatch, mocker):
    monkeypatch.setattr("app.config.settings.google_fact_check_api_key", "test_key")
    
    mock_response_data = {
        "claims": [
            {
                "text": "The sky is green.",
                "claimant": "Someone",
                "claimDate": "2023-01-01T00:00:00Z",
                "claimReview": [
                    {
                        "publisher": {"name": "Test Publisher"},
                        "url": "http://test-factcheck.com",
                        "title": "Fact check: Sky is green",
                        "reviewDate": "2023-01-02T00:00:00Z",
                        "textualRating": "False",
                        "languageCode": "en"
                    }
                ]
            }
        ]
    }
    
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            
        def json(self):
            return self.json_data
            
        def raise_for_status(self):
            pass

    async def mock_get(*args, **kwargs):
        return MockResponse(mock_response_data, 200)

    mocker.patch("httpx.AsyncClient.get", side_effect=mock_get)
    
    client = GoogleFactCheckClient()
    results = await client.search("sky")
    
    assert len(results) == 1
    assert results[0].claim_text == "The sky is green."
    assert results[0].rating == "False"
    assert results[0].publisher == "Test Publisher"
    assert results[0].url == "http://test-factcheck.com"

@pytest.mark.asyncio
async def test_factcheck_empty_result(monkeypatch, mocker):
    monkeypatch.setattr("app.config.settings.google_fact_check_api_key", "test_key")
    
    class MockResponseEmpty:
        def json(self): return {}
        def raise_for_status(self): pass

    async def mock_get_empty(*args, **kwargs): return MockResponseEmpty()

    mocker.patch("httpx.AsyncClient.get", side_effect=mock_get_empty)
    
    client = GoogleFactCheckClient()
    results = await client.search("no matches here")
    assert len(results) == 0
