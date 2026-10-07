# AI-Powered Misinformation & Fact-Checking Agent

## Current Phase
Phase 2 — Search & Retrieval Integrations

## Architecture
FastAPI
↓
API Layer
↓
Pydantic Models
↓
Tavily Search + Google Fact Check + ChromaDB RAG
↓
LangGraph State Foundation

## Installation
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment (Windows):
   ```bash
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

## Configuration
Copy `.env.example` to `.env` and fill in the keys:
- `TAVILY_API_KEY`: Required for live web search
- `GOOGLE_FACT_CHECK_API_KEY`: Required for Google Fact Check API
- `RAG_PERSIST_DIRECTORY`: Used by ChromaDB for local knowledge base (default: `./data/knowledge_base`)

## Testing
Run the test suite with:
```bash
python -m pytest
```

To manually verify search integrations, you can set your API keys in `.env` and hit the test endpoint:
```bash
curl "http://127.0.0.1:8000/api/search/test?query=hot+water"
```

