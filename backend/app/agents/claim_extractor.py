import json
from typing import List
from langchain_core.prompts import PromptTemplate
from app.agents.llm_setup import get_llm, extract_response_text
from app.models.schemas import ExtractedClaim
from app.utils.logging import get_logger

logger = get_logger(__name__)

EXTRACTOR_PROMPT = """You are a precise factual claim extractor. 
Extract all verifiable factual claims from the following text.
Break down complex sentences into individual claims.
Ignore conversational filler, opinions, and questions.

Output your response ONLY as a valid JSON object matching this schema:
{{
  "claims": [
    {{
      "id": "unique-id-1",
      "text": "The extracted claim",
      "checkable": true,
      "context": "Brief context"
    }}
  ]
}}

Input Text: {text}
"""

async def extract_claims(text: str) -> List[ExtractedClaim]:
    llm = get_llm()
    prompt = PromptTemplate.from_template(EXTRACTOR_PROMPT)
    
    chain = prompt | llm
    
    try:
        response = await chain.ainvoke({"text": text})
        content = extract_response_text(response)
        from app.utils.json_parser import parse_json_from_llm
        parsed = parse_json_from_llm(content)
        
        extracted = []
        for c in parsed.get("claims", []):
            extracted.append(ExtractedClaim(
                id=c["id"],
                text=c["text"],
                checkable=c.get("checkable", True),
                context=c.get("context", "")
            ))
            
        return extracted if extracted else [ExtractedClaim(id="extracted-1", text=text, checkable=True, context="Single claim")]
    except Exception as e:
        logger.error(f"Failed to extract claims: {e}")
        # Fallback to returning the whole text as one claim if parsing fails
        return [ExtractedClaim(
            id="fallback-1",
            text=text,
            checkable=True,
            context="Fallback extraction"
        )]
