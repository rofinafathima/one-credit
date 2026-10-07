import sys
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except RuntimeError as e:
    chromadb = None
    
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

class VectorStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.persist_directory = settings.rag_persist_directory
        self.client = None
        self.collection = None
        
        if chromadb is None:
            logger.error("ChromaDB is disabled due to environment limitations (e.g., SQLite version).")
            return
            
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized ChromaDB at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None

    def get_collection(self):
        if not self.collection:
            raise RuntimeError("ChromaDB collection is not initialized.")
        return self.collection

vector_store = VectorStore()
