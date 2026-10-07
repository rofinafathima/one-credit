from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, constr

class Verdict(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNVERIFIABLE = "UNVERIFIABLE"

class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ClaimInput(BaseModel):
    text: constr(min_length=1, max_length=2000, strip_whitespace=True) # type: ignore

class ExtractedClaim(BaseModel):
    id: str
    text: str
    checkable: bool
    context: Optional[str] = None

class Evidence(BaseModel):
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    retrieved_date: Optional[str] = None
    snippet: Optional[str] = None
    relevance_score: Optional[float] = None
    source_quality: Optional[str] = None
    supports_claim: Optional[bool] = None
    contradicts_claim: Optional[bool] = None
    evidence_summary: Optional[str] = None

class ClaimResult(BaseModel):
    claim: str
    verdict: Verdict
    confidence: Confidence
    summary: str
    reasoning: str
    supporting_evidence: List[Evidence]
    contradicting_evidence: List[Evidence]
    sources: List[str]
    checked_at: str

class FactCheckResponse(BaseModel):
    verification_id: Optional[str] = None
    claims: List[ClaimResult] = []
    status: str
    message: Optional[str] = None

class SearchResult(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None
    score: Optional[float] = None
    published_date: Optional[str] = None
    source: Optional[str] = None
    retrieved_at: str

class FactCheckResult(BaseModel):
    claim_text: Optional[str] = None
    publisher: Optional[str] = None
    rating: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    review_date: Optional[str] = None
    language: Optional[str] = None
    retrieved_at: str

class RagDocument(BaseModel):
    document_id: str
    title: str
    content: str
    source_url: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

