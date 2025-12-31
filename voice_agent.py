from typing import List
import logging
import json

from dotenv import load_dotenv
from livekit.agents import Agent, JobContext, AgentSession, WorkerOptions, cli, AutoSubscribe
from livekit.plugins import silero

from src.data_classes import AgentTasks, AgentSummary, UserData
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
                llm="openai/gpt-4.1-mini",
                tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
                vad=silero.VAD.load())
        self.selected_tasks = selected_tasks
        self.final_results = {}

    async def on_enter(self) -> None:
        # Sequence tasks based on choice.
        # Identify Task):
        if AgentTasks.identify in self.selected_tasks:
            confirmed = await IdentityConfirmationTask()
            self.final_results["identity_verified"] = confirmed

            if not confirmed:
                await self.session.say("I'm sorry, I can only discuss medical details with the patient. Have a good day.")
                return

        # Well being task
        if AgentTasks.wellbeing in self.selected_tasks:
            self.final_results["wellbeing"] = await WellbeingTask()

        # Medication check task
        if AgentTasks.medication_adherence in self.selected_tasks:
            self.final_results["medication"] = await MedicationTask()


        # Final Summary and Closure
        await self.session.say("Thank you for you time. We have recorded your responses and will notify your doctor if needed. Good Bye!!")

async def entrypoint(ctx: JobContext):
    # Mock Admin choice
    admin_config = [AgentTasks.identify, AgentTasks.wellbeing, AgentTasks.medication_adherence]

    # Mock data
    dummy_data = {}
    with open("./local/patient_details.json", "r") as file:
        dummy_data = json.load(file)

    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()

    userData = UserData(ctx=ctx, **dummy_data)

    session = AgentSession[UserData](
        userdata=userData,
        stt="assemblyai/universal-streaming",
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        vad=silero.VAD.load()
    )
    await session.start(
        agent=PatientCareAgent(selected_tasks=admin_config),
        room=ctx.room,
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))