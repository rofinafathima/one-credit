import json
from langchain_core.prompts import PromptTemplate
from app.agents.llm_setup import get_llm, extract_response_text
from app.models.schemas import ExtractedClaim, Evidence, Verdict, Confidence
from app.utils.logging import get_logger

logger = get_logger(__name__)

JUDGE_PROMPT = """You are a strictly objective fact-checking judge.
Evaluate the claim based ONLY on the provided evidence.

Claim: {claim}

Evidence:
{evidence_text}

Possible Verdicts: TRUE, FALSE, MISLEADING, UNVERIFIABLE
Possible Confidences: HIGH, MEDIUM, LOW

You MUST output ONLY a valid JSON object matching this exact schema, even if there is no evidence:
{{
  "verdict": "VERDICT_HERE",
  "confidence": "CONFIDENCE_HERE",
  "reasoning": "Detailed explanation of why this verdict was reached based on the evidence."
}}

If evidence is completely lacking or unreliable, return UNVERIFIABLE and explain that no evidence was provided. DO NOT GUESS.
NEVER output raw text, ONLY JSON.
"""

async def evaluate_verdict(claim: ExtractedClaim, evidence: list[Evidence]) -> dict:
    llm = get_llm()
    prompt = PromptTemplate.from_template(JUDGE_PROMPT)
    
    evidence_text = "\n\n".join([
        f"Source: {e.publisher} | URL: {e.source_url}\nContent: {e.snippet}" 
        for e in evidence[:10]  # Limit to top 10 for context window
    ])
    
    if not evidence_text.strip():
        evidence_text = "No evidence found."
    
    chain = prompt | llm
    
    response = None
    try:
        response = await chain.ainvoke({
            "claim": claim.text,
            "evidence_text": evidence_text
        })
        
        content = extract_response_text(response)
        from app.utils.json_parser import parse_json_from_llm
        return parse_json_from_llm(content)
    except Exception as e:
        logger.error(f"Failed to judge verdict: {e}")
        raw_text = extract_response_text(response) if response else str(e)
        return {
            "verdict": Verdict.UNVERIFIABLE.value,
            "confidence": Confidence.LOW.value,
            "reasoning": f"Error: {raw_text[:200]}..."
        }
