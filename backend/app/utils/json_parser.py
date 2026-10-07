import json
import re

def parse_json_from_llm(content) -> dict:
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
            else:
                text_parts.append(str(item))
        content = "\n".join(text_parts)
    elif not isinstance(content, str):
        content = str(content)

    content = content.strip()
    
    # Try direct parse
    try:
        return json.loads(content)
    except Exception:
        pass
        
    # Try finding markdown blocks
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            pass
            
    # Fallback to finding the first { and last }
    start = content.find('{')
    end = content.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(content[start:end+1])
        except Exception:
            pass
            
    raise ValueError(f"Could not parse JSON from LLM response: {content}")
