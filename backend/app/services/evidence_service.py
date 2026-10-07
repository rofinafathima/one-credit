import datetime
import asyncio
from typing import List
from app.models.schemas import Evidence
from app.search.tavily_client import TavilySearchClient
from app.search.factcheck_client import GoogleFactCheckClient
from app.rag.retriever import search_knowledge_base
from app.utils.logging import get_logger

logger = get_logger(__name__)

class EvidenceService:
    def __init__(self):
        self.tavily_client = TavilySearchClient()
        self.factcheck_client = GoogleFactCheckClient()

    async def search_web(self, query: str, max_results: int = 5) -> List[Evidence]:
        try:
            results = await asyncio.to_thread(self.tavily_client.search, query, max_results=max_results)
            evidences = []
            for r in results:
                evidences.append(Evidence(
                    source_title=r.title,
                    source_url=r.url,
                    publisher=r.source,
                    publication_date=r.published_date,
                    retrieved_date=r.retrieved_at,
                    snippet=r.content,
                    relevance_score=r.score,
                    source_quality="UNKNOWN",
                    supports_claim=None,
                    contradicts_claim=None,
                    evidence_summary=None
                ))
            return evidences
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return []

    async def search_rag(self, query: str, top_k: int = 3) -> List[Evidence]:
        try:
            results = await asyncio.to_thread(search_knowledge_base, query, top_k=top_k)
            evidences = []
            for doc, score in results:
                evidences.append(Evidence(
                    source_title=doc.title,
                    source_url=doc.source_url,
                    publisher=doc.publisher,
                    publication_date=doc.publication_date,
                    retrieved_date=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    snippet=doc.content,
                    relevance_score=score,
                    source_quality="UNKNOWN",
                    supports_claim=None,
                    contradicts_claim=None,
                    evidence_summary=None
                ))
            return evidences
        except Exception as e:
            logger.error(f"Error in rag search: {e}")
            return []

    async def search_fact_checks(self, query: str) -> List[Evidence]:
        try:
            results = await self.factcheck_client.search(query)
            evidences = []
            for r in results:
                evidences.append(Evidence(
                    source_title=r.title,
                    source_url=r.url,
                    publisher=r.publisher,
                    publication_date=r.review_date,
                    retrieved_date=r.retrieved_at,
                    snippet=f"Rating: {r.rating} | Claim: {r.claim_text}",
                    relevance_score=None,
                    source_quality="UNKNOWN",
                    supports_claim=None,
                    contradicts_claim=None,
                    evidence_summary=None
                ))
            return evidences
        except Exception as e:
            logger.error(f"Error in fact check search: {e}")
            return []

evidence_service = EvidenceService()
