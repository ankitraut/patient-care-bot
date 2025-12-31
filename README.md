HealthVoiceBot
===============

A lightweight voice follow-up bot for hospitals using configurable tasks and LiveKit integration.

Quickstart
---------

1. Install dependencies (use a virtual environment):

```powershell
python -m pip install -r requirements.txt
```

2. Run the example runner to simulate an agent call:

```powershell
python src/runner.py
```

Files added/edited
------------------
- src/agents/voice_agent.py - Orchestration agent
- src/tasks/* - Task implementations (confirm_identity, ask_problems, med_adherence)
- src/tools/vector_store.py - FAISS-backed search wrapper
- src/integrations/livekit_client.py - LiveKit placeholder wrapper
- src/prompts/templates/*.j2 - Prompt templates in jinja2 with frontmatter
- src/prompts/prompt_manager.py - Fixed environment path bug

Notes
-----
- This repository uses simple rule-based parsing for transcripts. Replace with robust LLM parsing or NLU for production.
- The LiveKit integration is a skeleton and must be implemented with real SDK calls and token generation.

Requirements coverage
---------------------
- Agent orchestration: Done
- Configurable tasks: Done (configurable via AgentConfig.tasks)
- Confirm identity task: Done
- Ask problems task: Done
- Medication adherence task: Done
- Use patient runtime info: Done (agent.run accepts patient dict)
- Vector DB tool: Done (FAISS wrapper)
- Prompts under prompts/templates: Done
- Structured conversation summary: Done

Next steps
----------
- Hook up real LiveKit SDK to play TTS and capture audio.
- Use ASR model or service to transcribe audio into text for tasks.
- Add unit tests for tasks and agent.

