import datetime
from typing import List, Optional
from tavily import TavilyClient, MissingAPIKeyError, InvalidAPIKeyError
from app.config import settings
from app.models.schemas import SearchResult
from app.utils.logging import get_logger

logger = get_logger(__name__)

class TavilySearchClient:
    def __init__(self):
        self.api_key = settings.tavily_api_key
        if not self.api_key:
            logger.error("TAVILY_API_KEY is missing from configuration")
        else:
            try:
                self.client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Error initializing TavilyClient: {e}")
                self.client = None

    def search(self, query: str, max_results: int = 5, topic: str = "general", search_depth: str = "basic") -> List[SearchResult]:
        if not self.api_key or not getattr(self, "client", None):
            raise ValueError("Tavily API key is not configured properly.")
            
        try:
            response = self.client.search(
                query=query, 
                max_results=max_results,
                topic=topic,
                search_depth=search_depth
            )
            return self._normalize_results(response.get("results", []))
        except MissingAPIKeyError:
            logger.error("Missing Tavily API key.")
            raise ValueError("Tavily API key is missing.")
        except InvalidAPIKeyError:
            logger.error("Invalid Tavily API key.")
            raise ValueError("Tavily API key is invalid.")
        except Exception as e:
            logger.error(f"Error during Tavily search: {e}")
            raise RuntimeError(f"Tavily search failed: {str(e)}")

    def _normalize_results(self, raw_results: List[dict]) -> List[SearchResult]:
        normalized = []
        retrieved_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        for item in raw_results:
            normalized.append(SearchResult(
                title=item.get("title"),
                url=item.get("url"),
                content=item.get("content"),
                score=item.get("score"),
                published_date=item.get("published_date"),
                source=item.get("source"),
                retrieved_at=retrieved_at
            ))
        return normalized
