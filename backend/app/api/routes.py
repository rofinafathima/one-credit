from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schemas import ClaimInput, FactCheckResponse
from app.services.evidence_service import evidence_service
from app.graph.workflow import fact_check_graph
from app.models.database import get_db, VerificationRun, ClaimRecord, EvidenceRecord
import uuid
import datetime

router = APIRouter()

@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(claim: ClaimInput, db: Session = Depends(get_db)):
    # Run the graph
    initial_state = {
        "original_input": claim.text,
        "claims": [],
        "current_claim": None,
        "claim_index": 0,
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "sources": [],
        "verdict": None,
        "confidence": None,
        "reasoning": None,
        "critic_feedback": None,
        "reflection_round": 0,
        "final_results": [],
        "errors": []
    }
    
    final_state = await fact_check_graph.ainvoke(initial_state)
    
    run_id = str(uuid.uuid4())
    
    # Save to database
    db_run = VerificationRun(id=run_id, status="success")
    db.add(db_run)
    db.commit()
    
    for c_res in final_state.get("final_results", []):
        db_claim = ClaimRecord(
            run_id=run_id,
            claim_text=c_res.claim,
            verdict=c_res.verdict.value,
            confidence=c_res.confidence.value,
            summary=c_res.summary,
            reasoning=c_res.reasoning,
            checked_at=datetime.datetime.utcnow()
        )
        db.add(db_claim)
        db.commit()
        db.refresh(db_claim)
        
        for ev in c_res.supporting_evidence:
            db_ev = EvidenceRecord(
                claim_id=db_claim.id,
                source_title=ev.source_title,
                source_url=ev.source_url,
                publisher=ev.publisher,
                snippet=ev.snippet,
                evidence_type="SUPPORTING"
            )
            db.add(db_ev)
            
        for ev in c_res.contradicting_evidence:
            db_ev = EvidenceRecord(
                claim_id=db_claim.id,
                source_title=ev.source_title,
                source_url=ev.source_url,
                publisher=ev.publisher,
                snippet=ev.snippet,
                evidence_type="CONTRADICTING"
            )
            db.add(db_ev)
            
        db.commit()
    
    return FactCheckResponse(
        verification_id=run_id,
        claims=final_state.get("final_results", []),
        status="success",
        message="Fact check complete."
    )

from pydantic import BaseModel
class DigestRequest(BaseModel):
    topic: str

@router.post("/digest")
async def create_digest(req: DigestRequest):
    from app.agents.digest_writer import generate_digest
    digest_md = await generate_digest(req.topic)
    return {"status": "success", "digest": digest_md}

@router.get("/search/test")
async def search_test(query: str):
    """
    DEVELOPMENT ENDPOINT ONLY
    Test the retrieval layer. Does NOT produce verdicts.
    """
    web_results = await evidence_service.search_web(query, max_results=2)
    rag_results = await evidence_service.search_rag(query, top_k=2)
    factcheck_results = await evidence_service.search_fact_checks(query)
    
    return {
        "status": "success",
        "message": "Retrieval endpoints tested. NO VERDICT PRODUCED.",
        "data": {
            "web_results": web_results,
            "rag_results": rag_results,
            "factcheck_results": factcheck_results
        }
    }
