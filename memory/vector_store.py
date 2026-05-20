"""Vector store implementation for GIDBoy memory.

Supports ChromaDB as the primary vector database,
with fallback to in-memory storage for development.
"""
from typing import List, Dict, Any, Optional
import json
import os


class VectorStore:
    """Base vector store interface."""

    def __init__(self, collection_name: str = "gidboy_memory"):
        self.collection_name = collection_name

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Add texts to the vector store."""
        raise NotImplementedError

    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar texts."""
        raise NotImplementedError

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        raise NotImplementedError


class ChromaDBStore(VectorStore):
    """ChromaDB vector store implementation."""

    def __init__(self, collection_name: str = "gidboy_memory", persist_dir: str = "./chroma_db"):
        super().__init__(collection_name)
        self.persist_dir = persist_dir
        self.client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        """Initialize ChromaDB client."""
        try:
            import chromadb
            from chromadb.config import Settings

            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_dir,
                anonymized_telemetry=False
            ))

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "GIDBoy research memory"}
            )

            print(f"ChromaDB initialized: {self.collection_name}")
        except ImportError:
            print("Warning: ChromaDB not installed, falling back to memory storage")
            self.client = None
        except Exception as e:
            print(f"ChromaDB initialization failed: {e}")
            self.client = None

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Add texts to ChromaDB."""
        if not self.collection:
            return

        try:
            ids = [str(i) for i in range(len(texts))]
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            # Persist to disk
            if hasattr(self.client, 'persist'):
                self.client.persist()
        except Exception as e:
            print(f"Failed to add texts to ChromaDB: {e}")

    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search ChromaDB for similar texts."""
        if not self.collection:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )

            # Format results
            formatted = []
            for i in range(len(results.get("documents", [[]])[0])):
                formatted.append({
                    "query": results["metadatas"][0][i].get("query", ""),
                    "response": results["documents"][0][i],
                    "mode": results["metadatas"][0][i].get("mode", "unknown"),
                    "timestamp": results["metadatas"][0][i].get("timestamp", ""),
                    "score": results.get("distances", [[]])[0][i] if results.get("distances") else 0
                })

            return formatted
        except Exception as e:
            print(f"ChromaDB search failed: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.collection:
            return {"status": "not_initialized"}

        try:
            count = self.collection.count()
            return {
                "status": "active",
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_dir": self.persist_dir
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


class InMemoryVectorStore(VectorStore):
    """In-memory vector store for development/testing."""

    def __init__(self, collection_name: str = "gidboy_memory"):
        super().__init__(collection_name)
        self.documents = []
        self.metadatas = []

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Add texts to memory."""
        for text, metadata in zip(texts, metadatas):
            self.documents.append(text)
            self.metadatas.append(metadata)

    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Simple keyword-based search."""
        query_words = set(query.lower().split())
        scored = []

        for i, doc in enumerate(self.documents):
            doc_words = set(doc.lower().split())
            score = len(query_words & doc_words)
            if score > 0:
                scored.append((score, i))

        scored.sort(reverse=True)
        top_k = scored[:k]

        results = []
        for score, idx in top_k:
            results.append({
                "query": self.metadatas[idx].get("query", ""),
                "response": self.documents[idx],
                "mode": self.metadatas[idx].get("mode", "unknown"),
                "timestamp": self.metadatas[idx].get("timestamp", ""),
                "score": score
            })

        return results

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            "status": "in_memory",
            "collection_name": self.collection_name,
            "document_count": len(self.documents)
        }


def create_vector_store(
    collection_name: str = "gidboy_memory",
    persist_dir: str = "./chroma_db",
    prefer_chroma: bool = True
) -> VectorStore:
    """Factory function to create appropriate vector store."""
    if prefer_chroma:
        chroma = ChromaDBStore(collection_name, persist_dir)
        if chroma.client:
            return chroma

    return InMemoryVectorStore(collection_name)
