import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_keys():
    print("Testing Tavily Key...")
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        print("❌ Tavily key is missing.")
    else:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_key)
            client.search("test", search_depth="basic")
            print("[SUCCESS] Tavily key is VALID.")
        except Exception as e:
            print(f"[ERROR] Tavily key is INVALID: {e}")

    print("\nTesting LLM Key...")
    llm_key = os.getenv("LLM_API_KEY")
    if not llm_key:
        print("[ERROR] LLM key is missing.")
    else:
        if llm_key.startswith("sk-"):
            print("Detected OpenAI key format. Testing...")
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(api_key=llm_key, model="gpt-4o-mini")
                llm.invoke("Say hello")
                print("[SUCCESS] OpenAI key is VALID.")
            except Exception as e:
                print(f"[ERROR] OpenAI key is INVALID: {e}")
        else:
            print("Testing as Gemini key...")
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(google_api_key=llm_key, model="gemini-1.5-pro")
                llm.invoke("Say hello")
                print("[SUCCESS] Gemini key is VALID.")
            except Exception as e:
                print(f"[ERROR] Gemini key is INVALID: {e}")

if __name__ == "__main__":
    asyncio.run(test_keys())
