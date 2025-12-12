# Filesystem Agent

This project is a small playground for testing a LangChain + DeepAgents workflow that
organizes files into semantic folders. A `FileAgent` reads the contents of a workspace,
creates category folders (e.g., `work`, `private`), and uses a custom move tool to relocate
files into the correct destination.

## Prerequisites

- Dev container (VS Code Remote Containers or GitHub Codespaces works best)
- Python 3.13 (handled automatically inside the dev container)
- [Poetry](https://python-poetry.org/)
- OpenAI API key (set `LLM_API_KEY` or edit `app/core/config.yml`)

## Setup

1. Open the repo inside the dev container.
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Set your API key (choose one):
   - Environment variable:
     ```bash
     export LLM_API_KEY=sk-...
     ```
   - Or edit `app/core/config.yml` under `api.key`.

## How It Works

- `app/services/data.py` provides `initialize_agent_data()` which wipes and repopulates
  `app/data/agent_workspace` with sample work/private documents.
- `app/services/agent.py` defines `FileAgent`. It:
  - Initializes a LangChain chat model with config-driven credentials.
  - Registers a custom `move_file` tool that only operates inside the repo.
  - Builds a DeepAgent with a filesystem backend so the agent can inspect and mutate files.
  - Exposes `organize(root, semantics)` which asks the agent to create folders and move files
    according to a JSON semantics map.

## Running the Agent

With dependencies installed and the API key set:

```bash
poetry run python -m app.services.agent
```

This will:

1. Reset `app/data/agent_workspace` to a known state.
2. Invoke `FileAgent.organize` with semantics:
   ```json
   {
     "work": "Documents related to professional projects, planning, clients, or company meetings.",
     "private": "Personal files such as travel plans, recipes, or family finances."
   }
   ```
3. Print the agent’s summary once it finishes organizing.

## Debugging

Use the VS Code launch config `Run FileAgent` (`.vscode/launch.json`). It sets `PYTHONPATH`
so imports work inside the debugger. Remember to run `initialize_agent_data()` (the script
does this automatically) if you want a clean workspace before each debug session.
