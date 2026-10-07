import httpx
import datetime
from typing import List, Optional
from app.config import settings
from app.models.schemas import FactCheckResult
from app.utils.logging import get_logger

logger = get_logger(__name__)

class GoogleFactCheckClient:
    def __init__(self):
        self.api_key = settings.google_fact_check_api_key
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    async def search(self, query: str) -> List[FactCheckResult]:
        if not self.api_key:
            raise ValueError("GOOGLE_FACT_CHECK_API_KEY is missing from configuration.")
            
        params = {
            "query": query,
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                return self._normalize_results(data.get("claims", []))
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Google Fact Check API: {e}")
            raise RuntimeError(f"Fact Check API HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error from Google Fact Check API: {e}")
            raise RuntimeError("Network error connecting to Fact Check API.")
        except Exception as e:
            logger.error(f"Unexpected error in Google Fact Check client: {e}")
            raise RuntimeError(f"Unexpected error: {str(e)}")

    def _normalize_results(self, raw_claims: List[dict]) -> List[FactCheckResult]:
        normalized = []
        retrieved_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        for claim in raw_claims:
            claim_text = claim.get("text")
            claimant = claim.get("claimant")
            claim_date = claim.get("claimDate")
            
            for review in claim.get("claimReview", []):
                publisher = review.get("publisher", {}).get("name")
                rating = review.get("textualRating")
                title = review.get("title")
                url = review.get("url")
                review_date = review.get("reviewDate")
                language = review.get("languageCode")
                
                normalized.append(FactCheckResult(
                    claim_text=claim_text,
                    publisher=publisher,
                    rating=rating,
                    title=title,
                    url=url,
                    review_date=review_date,
                    language=language,
                    retrieved_at=retrieved_at
                ))
        return normalized
