import datetime
from typing import TypedDict, cast
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.agents.claim_extractor import extract_claims
from app.agents.evidence_retriever import retrieve_evidence
from app.agents.verdict_judge import evaluate_verdict
from app.agents.critic import review_verdict
from app.models.schemas import ClaimResult, Verdict, Confidence

async def node_extract(state: AgentState):
    claims = await extract_claims(state["original_input"])
    return {"claims": claims, "claim_index": 0, "final_results": [], "errors": []}

def node_check_completion(state: AgentState):
    pass

async def node_retrieve(state: AgentState):
    claim = state["claims"][state["claim_index"]]
    evidence, sources = await retrieve_evidence(claim)
    
    return {
        "current_claim": claim, 
        "supporting_evidence": evidence,
        "contradicting_evidence": [],
        "sources": sources
    }

async def node_judge(state: AgentState):
    claim = state["current_claim"]
    evidence = state["supporting_evidence"] + state["contradicting_evidence"]
    
    result = await evaluate_verdict(claim, evidence)
    
    return {
        "verdict": Verdict(result.get("verdict", "UNVERIFIABLE")),
        "confidence": Confidence(result.get("confidence", "LOW")),
        "reasoning": result.get("reasoning", "")
    }

async def node_critic(state: AgentState):
    claim = state["current_claim"]
    result = await review_verdict(claim.text, state["verdict"].value, state["reasoning"])
    
    new_round = state.get("reflection_round", 0) + 1
    
    return {
        "critic_feedback": result.get("feedback", ""),
        "reflection_round": new_round,
        "_critic_approved": result.get("approved", True),
        "_needs_more": result.get("needs_more_evidence", False)
    }

def node_finalize_claim(state: AgentState):
    claim = state["current_claim"]
    
    result = ClaimResult(
        claim=claim.text,
        verdict=state["verdict"],
        confidence=state["confidence"],
        summary=f"Checked: {claim.text[:30]}...",
        reasoning=state["reasoning"],
        supporting_evidence=state["supporting_evidence"],
        contradicting_evidence=state["contradicting_evidence"],
        sources=state["sources"],
        checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    
    final_results = state.get("final_results", [])
    final_results.append(result)
    
    return {
        "final_results": final_results,
        "claim_index": state["claim_index"] + 1,
        "reflection_round": 0
    }

def should_reflect(state: AgentState):
    approved = state.get("_critic_approved", True)
    round_num = state.get("reflection_round", 0)
    
    # Fast path: max 1 reflection round
    if not approved and round_num < 1:
        return "retrieve"
    return "finalize"

def should_continue(state: AgentState):
    idx = state.get("claim_index", 0)
    claims = state.get("claims", [])
    if idx < len(claims):
        return "retrieve"
    return END

def build_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("extract", node_extract)
    workflow.add_node("retrieve", node_retrieve)
    workflow.add_node("judge", node_judge)
    workflow.add_node("critic", node_critic)
    workflow.add_node("finalize_claim", node_finalize_claim)
    
    workflow.set_entry_point("extract")
    
    workflow.add_conditional_edges(
        "extract",
        should_continue,
        {"retrieve": "retrieve", END: END}
    )
    
    workflow.add_edge("retrieve", "judge")
    workflow.add_edge("judge", "critic")
    
    workflow.add_conditional_edges(
        "critic",
        should_reflect,
        {"retrieve": "retrieve", "finalize": "finalize_claim"}
    )
    
    workflow.add_conditional_edges(
        "finalize_claim",
        should_continue,
        {"retrieve": "retrieve", END: END}
    )
    
    return workflow.compile()

fact_check_graph = build_workflow()
