import json
import traceback

from livekit.agents import AgentTask, function_tool
from livekit.agents.llm.tool_context import ToolError

from src.data_classes import MedicationStatus
from src.prompts.prompt_manager import PromptManager
from src.tools.agent_tools import Tools


class MedicationTask(AgentTask[MedicationStatus]):
    """Task to check medication adherence with tool support"""

    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions=PromptManager.get_prompt("med_adherence_instructions"),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=PromptManager.get_prompt("med_adherence",
                                                  prescription=self.session.userdata.prescription),

        )

    @function_tool()
    async def medication_status_summary(self, medication_summary: str) -> None | ToolError:
        """Use this tool when you have all the information and are ready to record the summary of the
        interaction with the patient."""
        try:
            summary = json.loads(medication_summary)
            self.complete(
                MedicationStatus(
                    **summary
                )
            )
        except:
            return ToolError(traceback.format_exc())
