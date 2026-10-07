from typing import List, Tuple
from app.models.schemas import RagDocument
from app.rag.vector_store import vector_store
from app.utils.logging import get_logger

logger = get_logger(__name__)

def search_knowledge_base(query: str, top_k: int = 5) -> List[Tuple[RagDocument, float]]:
    try:
        collection = vector_store.get_collection()
    except Exception as e:
        logger.error(f"Cannot search knowledge base: {e}")
        return []

    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        logger.error(f"Error querying ChromaDB: {e}")
        return []
        
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    
    rag_results = []
    
    for i in range(len(documents)):
        doc_content = documents[i]
        meta = metadatas[i] or {}
        distance = distances[i]
        # In cosine distance, smaller is closer. Score could be inverted, but we just pass distance for now
        # or calculate a similarity score: 1.0 - distance
        similarity_score = 1.0 - distance
        
        # Only return reasonably close matches if we had a threshold, but for now just return top_k
        
        doc = RagDocument(
            document_id=results["ids"][0][i],
            title=meta.get("title", "Unknown Title"),
            content=doc_content,
            source_url=meta.get("source_url"),
            publisher=meta.get("publisher"),
            publication_date=meta.get("publication_date"),
            category=meta.get("category"),
            metadata=meta
        )
        
        rag_results.append((doc, similarity_score))
        
    return rag_results
