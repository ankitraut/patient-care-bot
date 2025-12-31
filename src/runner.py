from src.agents.voice_agent import VoiceAgent, AgentConfig


def example_run():
    config = AgentConfig(tasks=["confirm_identity", "ask_problems", "med_adherence"])
    agent = VoiceAgent(config)

    patient = {
        "name": "John Doe",
        "age": 68,
        "address": "123 Main St",
        "medications": [{"name": "Atenolol", "dose": "50mg twice daily"}, {"name": "Metformin", "dose": "500mg twice a day"}],
    }

    # Simulated ASR transcripts for tasks keyed by task name
    call_audio = {
        "confirm_identity": "Hello, this is John Doe",
        "ask_problems": "Chest pain: severe; dizziness: mild",
        "med_adherence": "I missed Atenolol yesterday; I take Metformin twice a day",
    }

    result = agent.run(patient, call_audio=call_audio)
    print(result["rendered_summary"])


if __name__ == "__main__":
    example_run()
