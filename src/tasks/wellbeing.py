from livekit.agents import AgentTask

from src.data_classes import HealthStatus
from src.prompts.prompt_manager import PromptManager


class WellbeingTask(AgentTask[HealthStatus]):
    """Task to check health problems and classify severity"""
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions=PromptManager.get_prompt("wellbeing"),
            chat_ctx=chat_ctx
            # TODO: output_type?
        )

    async def on_enter(self) -> None:
        await self.session.say("How have you been feeling since you returned home? Any new symptoms or concerns?")

