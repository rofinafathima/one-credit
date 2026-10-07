import json
from typing import Dict, Any, List, Tuple
from langchain_core.prompts import PromptTemplate
from app.agents.llm_setup import get_llm, extract_response_text
from app.models.schemas import ExtractedClaim, Evidence
from app.services.evidence_service import evidence_service
from app.utils.logging import get_logger

logger = get_logger(__name__)

QUERY_GENERATOR_PROMPT = """You are a search query generator for fact-checking.
Generate 3 optimized search queries for the following claim:
1. A neutral query to find general evidence
2. A query optimized to find supporting evidence
3. A query optimized to find contradicting evidence

Output ONLY a JSON object:
{{
  "neutral": "...",
  "supporting": "...",
  "contradicting": "..."
}}

Claim: {claim}
"""

import asyncio

async def retrieve_evidence(claim: ExtractedClaim) -> Tuple[List[Evidence], List[str]]:
    llm = get_llm()
    prompt = PromptTemplate.from_template(QUERY_GENERATOR_PROMPT)
    chain = prompt | llm
    
    try:
        response = await chain.ainvoke({"claim": claim.text})
        content = extract_response_text(response)
        from app.utils.json_parser import parse_json_from_llm
        queries = parse_json_from_llm(content)
    except Exception as e:
        logger.error(f"Failed to generate queries: {e}")
        queries = {
            "neutral": f"{claim.text} evidence",
            "supporting": f"{claim.text}",
            "contradicting": f"{claim.text} false debunked"
        }
    
    all_evidence: List[Evidence] = []
    sources = set()
    
    # Launch all searches in parallel across queries and search backends
    tasks = []
    for q_type, q_string in queries.items():
        tasks.append(evidence_service.search_web(q_string))
        tasks.append(evidence_service.search_rag(q_string))
        tasks.append(evidence_service.search_fact_checks(q_string))
        
    search_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for res in search_results:
        if isinstance(res, list):
            all_evidence.extend(res)
        elif isinstance(res, Exception):
            logger.error(f"Search task raised exception: {res}")
            
    for ev in all_evidence:
        if ev.source_url:
            sources.add(ev.source_url)
            
    return all_evidence, list(sources)
