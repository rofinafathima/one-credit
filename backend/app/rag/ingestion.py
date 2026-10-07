import uuid
from typing import Dict, Any, Optional
from app.models.schemas import RagDocument
from app.rag.vector_store import vector_store
from app.utils.logging import get_logger

logger = get_logger(__name__)

def ingest_document(title: str, content: str, source_url: Optional[str] = None, 
                    publisher: Optional[str] = None, publication_date: Optional[str] = None,
                    category: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> RagDocument:
    
    document_id = str(uuid.uuid4())
    meta = metadata or {}
    
    doc = RagDocument(
        document_id=document_id,
        title=title,
        content=content,
        source_url=source_url,
        publisher=publisher,
        publication_date=publication_date,
        category=category,
        metadata=meta
    )
    
    # Store into ChromaDB
    collection = vector_store.get_collection()
    
    # Flatten metadata for ChromaDB compatibility
    chroma_meta = {
        "title": title,
        "source_url": source_url or "",
        "publisher": publisher or "",
        "publication_date": publication_date or "",
        "category": category or "",
    }
    # Add any flat string/int/float from metadata
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)):
            chroma_meta[k] = v

    try:
        collection.add(
            documents=[content],
            metadatas=[chroma_meta],
            ids=[document_id]
        )
        logger.info(f"Ingested document {document_id} into knowledge base.")
    except Exception as e:
        logger.error(f"Error ingesting document to ChromaDB: {e}")
        raise RuntimeError(f"Failed to ingest document: {e}")
        
    return doc
