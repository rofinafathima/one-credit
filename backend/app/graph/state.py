from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from app.models.schemas import ExtractedClaim, Evidence, Verdict, Confidence, ClaimResult

class AgentState(TypedDict):
    original_input: str
    claims: List[ExtractedClaim]
    current_claim: Optional[ExtractedClaim]
    claim_index: int
    supporting_evidence: List[Evidence]
    contradicting_evidence: List[Evidence]
    sources: List[str]
    verdict: Optional[Verdict]
    confidence: Optional[Confidence]
    reasoning: Optional[str]
    critic_feedback: Optional[str]
    reflection_round: int
    final_results: List[ClaimResult]
    errors: List[str]
