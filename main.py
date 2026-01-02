from typing import List
import logging
import json

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    JobContext,
    AgentSession,
    WorkerOptions,
    cli,
    AutoSubscribe,
)
from livekit.plugins import silero

from src.data_classes import AgentTasks, AgentSummary, UserData
from src.tasks.confirm_identity import IdentityConfirmationTask
from src.tasks.med_adherence import MedicationTask
from src.tasks.wellbeing import WellbeingTask
from src.agents.voice_agent import PatientCareAgent


logger = logging.getLogger("patient-care-agent")
logger.setLevel(logging.INFO)

load_dotenv()


async def entrypoint(ctx: JobContext):
    # Mock Admin choice
    admin_config = [
        AgentTasks.identify,
        AgentTasks.wellbeing,
        AgentTasks.medication_adherence,
    ]

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
        llm="openai/gpt-5-nano",
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        vad=silero.VAD.load(),
    )
    await session.start(
        agent=PatientCareAgent(selected_tasks=admin_config),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
