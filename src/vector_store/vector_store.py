from typing import List, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    """Simple FAISS-backed vector store for semantic search."""

    def __init__(self, index_path: Optional[str] = None, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.index_path = index_path
        if index_path:
            try:
                self.index = faiss.read_index(index_path)
            except Exception:
                self.index = None

    def add_documents(self, texts: List[str], metadatas: List[dict] = None):
        vectors = self.model.encode(texts, convert_to_numpy=True)
        if self.index is None:
            dim = vectors.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(vectors)
        if metadatas:
            self.documents.extend(metadatas)
        else:
            self.documents.extend([{"text": t} for t in texts])

    def search(self, query: str, k: int = 5):
        vec = self.model.encode([query], convert_to_numpy=True)
        if self.index is None or self.index.ntotal == 0:
            return []
        D, I = self.index.search(vec, k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            meta = self.documents[idx] if idx < len(self.documents) else {"_missing": True}
            results.append({"score": float(dist), "metadata": meta})
        return results

    def save(self, path: str):
        if self.index is not None:
            faiss.write_index(self.index, path)
            self.index_path = path

