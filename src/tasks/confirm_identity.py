from livekit.agents import AgentTask, function_tool
from src.prompts.prompt_manager import PromptManager


class IdentityConfirmationTask(AgentTask[bool]):
    """Task to verify the patient is person talking"""

    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions=PromptManager.get_prompt("greeting_instructions"),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.say(
            PromptManager.get_prompt(
                "greeting",
                hospital_name=self.session.userdata.hospital_name,
                patient_name=self.session.userdata.patient_name,
            )
        )

    @function_tool()
    async def user_identity_confirmed(self) -> None:
        """Use this when the person speaking has confirmed they are indeed the patient"""
        self.complete(True)

    @function_tool()
    async def user_identity_denied(self) -> None:
        """Use this when the person speaking is not the patient"""
        self.complete(False)
