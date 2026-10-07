from langchain_core.prompts import PromptTemplate
from app.agents.llm_setup import get_llm
from app.services.evidence_service import evidence_service
from app.mcp.tools import save_digest_tool, export_markdown_tool
from app.utils.logging import get_logger
import datetime

logger = get_logger(__name__)

DIGEST_PROMPT = """You are a professional Digest Writer for a fact-checking organization.
Write a concise, highly readable daily digest on the topic: {topic}.

Use the following news/evidence as your source material:
{evidence_text}

Format your response in Markdown. Include:
1. A catchy title.
2. A summary of the top verified news.
3. Bullet points of key facts.
4. (Do NOT invent facts; only use the provided evidence).
"""

async def generate_digest(topic: str) -> str:
    llm = get_llm()
    prompt = PromptTemplate.from_template(DIGEST_PROMPT)
    
    # 1. Gather recent news/evidence on the topic
    news_evidence = await evidence_service.search_web(f"{topic} latest news")
    
    evidence_text = "\n\n".join([
        f"Source: {e.publisher} | URL: {e.source_url}\nContent: {e.snippet}" 
        for e in news_evidence[:15]
    ])
    
    if not evidence_text.strip():
        evidence_text = "No recent evidence found."
        
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "topic": topic,
            "evidence_text": evidence_text
        })
        digest_content = response.content.strip()
        
        # 2. Save using MCP tools internally
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        save_digest_tool(
            date=today_str,
            topic=topic,
            digest=digest_content,
            verified_claims=[]
        )
        
        export_markdown_tool(
            report_type="Daily Digest",
            content=digest_content,
            filename=f"digest_{topic.replace(' ', '_')}_{today_str}.md"
        )
        
        return digest_content
    except Exception as e:
        logger.error(f"Failed to generate digest: {e}")
        return f"Failed to generate digest: {str(e)}"
