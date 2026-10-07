from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

def get_llm():
    # Helper to get an LLM based on available keys
    if settings.llm_api_key.startswith("sk-") or settings.llm_api_key == "test_key":
        # Assume OpenAI key
        model_name = settings.llm_model if not settings.llm_model.startswith("gemini") else "gpt-4o-mini"
        return ChatOpenAI(
            api_key=settings.llm_api_key,
            model=model_name,
            temperature=0
        )
    elif settings.llm_api_key:
        # Assume Google Gemini key
        model_name = settings.llm_model if settings.llm_model.startswith("gemini") else "gemini-3.5-flash-lite"
        return ChatGoogleGenerativeAI(
            google_api_key=settings.llm_api_key,
            model=model_name,
            temperature=0,
            max_retries=1
        )
    else:
        # Default fallback
        return ChatOpenAI(api_key="fake-key", model="gpt-4o-mini")

def extract_response_text(response) -> str:
    if response is None:
        return ""
    if hasattr(response, "content"):
        content = response.content
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    texts.append(item["text"])
            return "\n".join(texts)
    return str(response)

