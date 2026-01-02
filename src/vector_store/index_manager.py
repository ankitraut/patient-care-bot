# file: src/vector_store/index_manager.py
import os
import json
import functools
from typing import List, Optional

from src.vector_store.vector_store import VectorStore


class IndexManager:
    """
    Manage multiple named FAISS indexes saved under a storage directory.
    - create_index(name, texts, metadatas) -> creates and saves index files
    - load_index(name) -> returns a VectorStore instance loaded from disk (cached)
    - list_indexes() -> list of available index names
    """

    def __init__(self, storage_dir: str = "indexes", model_name: str = "all-MiniLM-L6-v2", cache_size: int = 32):
        self.storage_dir = storage_dir
        self.model_name = model_name
        os.makedirs(self.storage_dir, exist_ok=True)

        # wrap the static loader with lru_cache so loaded VectorStore objects are reused
        self._load_cached = functools.lru_cache(maxsize=cache_size)(IndexManager._load_from_disk)

    def _paths(self, name: str):
        index_path = os.path.join(self.storage_dir, f"{name}.faiss")
        meta_path = os.path.join(self.storage_dir, f"{name}.meta.json")
        return index_path, meta_path

    def create_index(self, name: str, texts: List[str], metadatas: Optional[List[dict]] = None) -> None:
        """
        Create a new index from texts and optional metadatas and persist it.
        Overwrites existing files with the same name.
        Clears the cached loader so subsequent loads return the updated index.
        """
        index_path, meta_path = self._paths(name)
        store = VectorStore(index_path=None, model_name=self.model_name)
        store.add_documents(texts, metadatas)
        store.save(index_path)
        docs = metadatas if metadatas is not None else [{"text": t} for t in texts]
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)

        # Clear cache to avoid returning stale VectorStore instances
        self.clear_cache()

    def load_index(self, name: str) -> VectorStore:
        """
        Load an index by name. Uses an lru cache to avoid reloading on each query.
        Raises FileNotFoundError if missing.
        """
        index_path, meta_path = self._paths(name)
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found: {index_path}")
        # Call the cached loader
        return self._load_cached(index_path, meta_path, self.model_name)

    def list_indexes(self) -> List[str]:
        """
        Return available index names (without extensions) in the storage directory.
        """
        names = []
        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".faiss"):
                names.append(os.path.splitext(fname)[0])
        return sorted(names)

    def clear_cache(self) -> None:
        """
        Clear the LRU cache used for loading indexes.
        Call this after creating, updating or deleting indexes.
        """
        try:
            self._load_cached.cache_clear()
        except AttributeError:
            # No-op if cache not present
            pass

    @staticmethod
    def _load_from_disk(index_path: str, meta_path: str, model_name: str) -> VectorStore:
        """
        Static loader used by the cached wrapper. Keeps signature hashable for lru_cache.
        """
        store = VectorStore(index_path=index_path, model_name=model_name)
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                try:
                    store.documents = json.load(f)
                except Exception:
                    store.documents = []
        return store
