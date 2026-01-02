from typing import List
import logging
import json

from dotenv import load_dotenv
from livekit.agents import Agent
from livekit.plugins import silero

from src.data_classes import AgentTasks
from src.tasks.confirm_identity import IdentityConfirmationTask
from src.tasks.med_adherence import MedicationTask
from src.tasks.wellbeing import WellbeingTask


logger = logging.getLogger("patient-care-agent")
logger.setLevel(logging.INFO)

load_dotenv()


class PatientCareAgent(Agent):
    def __init__(self, selected_tasks: List[AgentTasks]):
        super().__init__(
            instructions="You are a medical follow-up agent. Be profession and empathetic.",
            stt="assemblyai/universal-streaming",
            llm="openai/gpt-5-nano",
            tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
            vad=silero.VAD.load(),
        )
        self.selected_tasks = selected_tasks
        self.final_results = {}

    async def on_enter(self) -> None:
        # Sequence tasks based on choice.
        # Identify Task:
        if AgentTasks.identify in self.selected_tasks:
            confirmed = await IdentityConfirmationTask(chat_ctx=self.chat_ctx)
            self.final_results["identity_verified"] = confirmed

            if not confirmed:
                await self.session.say(
                    "I'm sorry, I can only discuss medical details with the patient. Have a good day."
                )
                return

        # Well being task
        if AgentTasks.wellbeing in self.selected_tasks:
            self.final_results["wellbeing"] = await WellbeingTask(
                chat_ctx=self.chat_ctx
            )

        # Medication check task
        if AgentTasks.medication_adherence in self.selected_tasks:
            self.final_results["medication"] = await MedicationTask(
                chat_ctx=self.chat_ctx
            )

        # Final Summary and Closure
        await self.session.say(
            "Thank you for you time. We have recorded your responses and will notify your doctor if needed. Good Bye!!"
        )

        print(self.final_results)
