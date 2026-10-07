import pytest
from app.services.evidence_service import evidence_service
from app.models.schemas import Evidence

@pytest.mark.asyncio
async def test_evidence_service_normalization(mocker):
    # Mock the individual services to return known formats
    mocker.patch("app.services.evidence_service.TavilySearchClient.search", return_value=[])
    
    async def mock_search_fact_checks(query): return []
    mocker.patch("app.services.evidence_service.GoogleFactCheckClient.search", side_effect=mock_search_fact_checks)
    
    mocker.patch("app.services.evidence_service.search_knowledge_base", return_value=[])
    
    # Just testing that the wrappers don't blow up when returning empty
    web = await evidence_service.search_web("test")
    rag = await evidence_service.search_rag("test")
    fact = await evidence_service.search_fact_checks("test")
    
    assert isinstance(web, list)
    assert isinstance(rag, list)
    assert isinstance(fact, list)
