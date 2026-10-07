from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, VerificationRun, ClaimRecord, EvidenceRecord
from app.models.schemas import FactCheckResponse, ClaimResult, Evidence, Verdict, Confidence

router = APIRouter()

@router.get("/history", response_model=list[FactCheckResponse])
def get_history(db: Session = Depends(get_db)):
    runs = db.query(VerificationRun).order_by(VerificationRun.created_at.desc()).all()
    
    responses = []
    for run in runs:
        claims = []
        for c in run.claims:
            sup_ev = []
            con_ev = []
            sources = set()
            for e in c.evidence:
                ev_obj = Evidence(
                    source_title=e.source_title,
                    source_url=e.source_url,
                    publisher=e.publisher,
                    snippet=e.snippet
                )
                if e.evidence_type == "SUPPORTING":
                    sup_ev.append(ev_obj)
                else:
                    con_ev.append(ev_obj)
                if e.source_url:
                    sources.add(e.source_url)
                    
            claims.append(ClaimResult(
                claim=c.claim_text,
                verdict=Verdict(c.verdict),
                confidence=Confidence(c.confidence),
                summary=c.summary or "",
                reasoning=c.reasoning or "",
                supporting_evidence=sup_ev,
                contradicting_evidence=con_ev,
                sources=list(sources),
                checked_at=c.checked_at.isoformat() if c.checked_at else ""
            ))
            
        responses.append(FactCheckResponse(
            verification_id=run.id,
            claims=claims,
            status=run.status,
            message="Retrieved from history"
        ))
        
    return responses
