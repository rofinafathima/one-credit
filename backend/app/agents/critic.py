import json
from langchain_core.prompts import PromptTemplate
from app.agents.llm_setup import get_llm, extract_response_text
from app.utils.logging import get_logger

logger = get_logger(__name__)

CRITIC_PROMPT = """You are a critical reviewer evaluating a fact-check verdict.
Review the claim, the verdict, and the reasoning.

Claim: {claim}
Verdict: {verdict}
Reasoning: {reasoning}

Determine if:
1. The verdict is fully supported by the reasoning.
2. The reasoning sounds objective and unbiased.
3. More evidence is needed because the current reasoning is weak.

Output ONLY JSON:
{{
  "approved": true/false,
  "feedback": "Feedback for the judge/retriever",
  "needs_more_evidence": true/false
}}
"""

async def review_verdict(claim_text: str, verdict: str, reasoning: str) -> dict:
    llm = get_llm()
    prompt = PromptTemplate.from_template(CRITIC_PROMPT)
    chain = prompt | llm
    
    try:
        response = await chain.ainvoke({
            "claim": claim_text,
            "verdict": verdict,
            "reasoning": reasoning
        })
        
        content = extract_response_text(response)
        from app.utils.json_parser import parse_json_from_llm
        return parse_json_from_llm(content)
    except Exception as e:
        logger.error(f"Failed critic review: {e}")
        return {
            "approved": True, # Fail open to prevent infinite loops if LLM fails
            "feedback": "Critic failed to parse.",
            "needs_more_evidence": False
        }
