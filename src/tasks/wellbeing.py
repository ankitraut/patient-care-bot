import json
import traceback

from livekit.agents import AgentTask, function_tool
from livekit.agents.llm.tool_context import ToolError


from src.data_classes import HealthStatus
from src.prompts.prompt_manager import PromptManager


class WellbeingTask(AgentTask[HealthStatus]):
    """Task to check health problems and classify severity"""

    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions=PromptManager.get_prompt(
                "wellbeing",
                health_status_schema=HealthStatus.model_json_schema(),
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.say(
            "How have you been feeling since you returned home? Any new symptoms or concerns?"
        )

    @function_tool()
    async def patient_wellbeing_summary(self, wellbeing_summary: str) -> None | ToolError:
        """Use this to record the Summary of the patient's current condition/wellbeing
        wellbeing_summary: A dict representation of the HealthStatus class"""
        try:
            summary = json.loads(wellbeing_summary)
            self.complete(HealthStatus(
                **summary
            ))
        except:
            return ToolError(traceback.format_exc())
