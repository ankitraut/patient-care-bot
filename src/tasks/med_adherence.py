import json
import traceback
from typing import List, Dict, Any, Optional

from livekit.agents import AgentTask, function_tool
from livekit.agents.llm.tool_context import ToolError

from src.data_classes import MedicationStatus
from src.prompts.prompt_manager import PromptManager
from src.tools.agent_tools import Tools, IndexLookupTool, IndexQueryTool
from src.vector_store.index_manager import IndexManager


class MedicationTask(AgentTask[MedicationStatus]):
    """Task to check medication adherence with tool support"""

    def __init__(self, chat_ctx=None, index_manager: Optional[IndexManager] = None):
        super().__init__(
            instructions=PromptManager.get_prompt("med_adherence_instructions"),
            chat_ctx=chat_ctx,
        )
        self.index_manager = index_manager
        if index_manager:
            self._index_lookup = IndexLookupTool(index_manager)
            self._index_query = IndexQueryTool(index_manager)
        else:
            self._index_lookup = None
            self._index_query = None

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=PromptManager.get_prompt(
                "med_adherence", prescription=self.session.userdata.prescription
            ),
        )

    @function_tool()
    async def medication_status_summary(
        self, medication_summary: str
    ) -> None | ToolError:
        """Use this tool when you have all the information and are ready to record the summary of the
        interaction with the patient."""
        try:
            summary = json.loads(medication_summary)
            self.complete(MedicationStatus(**summary))
        except:
            return ToolError(traceback.format_exc())

    @function_tool(description="List available vector indexes")
    async def list_indexes(self) -> List[str] | ToolError:
        if not self._index_lookup:
            return ToolError("Index manager not configured")
        try:
            return await self._index_lookup.run()
        except Exception as e:
            return ToolError(str(e))

    @function_tool(description="Query a named index")
    async def query_index(
        self, index_name: str, query: str, k: int = 5
    ) -> List[Dict[str, Any]] | ToolError:
        if not self._index_query:
            return ToolError("Index manager not configured")
        try:
            return await self._index_query.run(index_name, query, k)
        except Exception as e:
            return ToolError(str(e))
