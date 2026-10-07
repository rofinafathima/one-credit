import pytest
from app.rag.ingestion import ingest_document
from app.rag.retriever import search_knowledge_base
from app.rag.vector_store import chromadb

@pytest.mark.skipif(chromadb is None, reason="ChromaDB requires newer SQLite3")
def test_rag_ingestion_and_retrieval(monkeypatch, tmp_path):
    # Use temporary directory for chroma db
    monkeypatch.setattr("app.config.settings.rag_persist_directory", str(tmp_path))
    
    # Needs to re-initialize vector_store to pick up new path
    from app.rag.vector_store import VectorStore
    VectorStore._instance = None # reset singleton
    
    doc = ingest_document(
        title="Test Rag Doc",
        content="This is a test document containing the keyword APPLE.",
        source_url="http://ragtest.com"
    )
    
    assert doc.title == "Test Rag Doc"
    assert doc.document_id is not None
    
    results = search_knowledge_base("APPLE")
    
    assert len(results) > 0
    retrieved_doc, score = results[0]
    assert retrieved_doc.title == "Test Rag Doc"
    assert retrieved_doc.content == "This is a test document containing the keyword APPLE."
    assert retrieved_doc.source_url == "http://ragtest.com"
