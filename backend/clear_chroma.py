import chromadb
from chromadb.config import Settings
import os

db_path = "./data/knowledge_base"
if os.path.exists(db_path):
    try:
        client = chromadb.PersistentClient(path=db_path, settings=Settings(allow_reset=True))
        # Drop the collection if it exists
        try:
            client.delete_collection("knowledge_base")
            print("Successfully deleted the knowledge_base collection to remove test data.")
        except Exception as e:
            print(f"Collection might not exist or could not be deleted: {e}")
    except Exception as e:
        print(f"Could not connect to Chroma: {e}")
else:
    print("No database found.")
