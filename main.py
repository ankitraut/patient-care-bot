from datetime import datetime
import logging
import json

from dotenv import load_dotenv
from livekit.agents import (
    JobContext,
    AgentSession,
    WorkerOptions,
    cli,
    AutoSubscribe,
)
from livekit.plugins import silero
from livekit.agents import AgentServer

from src.data_classes import AgentTasks, UserData
from src.agents.voice_agent import PatientCareAgent
from src.vector_store.index_manager import IndexManager

logger = logging.getLogger("patient-care-agent")
logger.setLevel(logging.INFO)

load_dotenv()


server = AgentServer()

async def on_session_end(ctx: JobContext) -> None:
    # Generate the full session report including transcripts
    report = ctx.make_session_report()
    report_dict = report.to_dict()

    # Save to a local JSON file
    filename = f"transcript_{ctx.room.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report_dict, f, indent=2)
    print(f"Transcript saved to {filename}")


@server.rtc_session(on_session_end=on_session_end)
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

    # index data
    index_manager = IndexManager(storage_dir="indexes", model_name="all-MiniLM-L6-v2")

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
        agent=PatientCareAgent(
            selected_tasks=admin_config, index_manager=index_manager
        ),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
