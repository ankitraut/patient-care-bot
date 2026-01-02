from livekit.agents import llm, function_tool


class Tools(llm.ToolContext):
    @function_tool(description="Lookup dosage or instructions for a medicine")
    def get_medicine_info(self, medicine_name: str) -> str:
        mock_db = {"paracetemol": "10 mg daily"}
        return mock_db.get(
            medicine_name.lower(), "No information found. Please Consult your doctor"
        )


# file: src/vector_store/tools.py
import asyncio
from typing import List, Dict, Any

from src.vector_store.index_manager import IndexManager


class IndexLookupTool:
    """
    Simple tool to list available index names.
    Usage: await IndexLookupTool(manager).run()
    """

    def __init__(self, manager: IndexManager):
        self.manager = manager

    async def run(self) -> List[str]:
        # Keep async-compatible for use inside LiveKit agents
        return await asyncio.to_thread(self.manager.list_indexes)


class IndexQueryTool:
    """
    Tool to query a named index.
    Usage: await IndexQueryTool(manager).run(index_name, query, k=5)
    Returns a list of results: [{ 'score': float, 'metadata': {...} }, ...]
    """

    def __init__(self, manager: IndexManager):
        self.manager = manager

    async def run(self, index_name: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        def _q():
            store = self.manager.load_index(index_name)
            return store.search(query, k=k)

        return await asyncio.to_thread(_q)