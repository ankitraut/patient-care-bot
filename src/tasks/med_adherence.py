from livekit.agents import AgentTask

from src.data_classes import MedicationStatus
from src.prompts.prompt_manager import PromptManager
from src.tools.agent_tools import Tools


class MedicationTask(AgentTask[MedicationStatus]):
    """Task to check medication adherence with tool support"""
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions=PromptManager.get_prompt("med_adherence"),
            chat_ctx=chat_ctx,
            tools=[Tools()] # TODO: check
        )

    async def on_enter(self) -> None:
        await self.session.say("I'd like to check on your medication. Are you able to take them as prescribed?")
