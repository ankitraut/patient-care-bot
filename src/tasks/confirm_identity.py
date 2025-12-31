from livekit.agents import AgentTask
from src.prompts.prompt_manager import PromptManager


class IdentityConfirmationTask(AgentTask[bool]):
    """Task to verify the patient is person talking"""
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions=PromptManager.get_prompt("confirm_identity"),
            chat_ctx=chat_ctx
        )

    async def on_enter(self) -> None:
        await self.session.say(
            PromptManager.get_prompt("greeting")
        )
