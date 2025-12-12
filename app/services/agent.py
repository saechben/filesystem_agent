from typing import Protocol, runtime_checkable
from pathlib import Path
import json
import shutil

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.chat_models import init_chat_model
from omegaconf import OmegaConf

from app.core.config import API_KEY_ENV_VAR, get_config
from app.services.data import initialize_agent_data

@runtime_checkable
class AgentInterface(Protocol):
    def organize(self,root:Path,semantics:dict):
        """
        organizes the files based on the given semantics
        
        :param root: Description
        :type root: Path
        :param semantics: contains information on folders and what they should contain to help the agent organize
        :type semantics: dict
        """

class FileAgent(AgentInterface):
    def __init__(self):
        self.workspace_root = Path(__file__).resolve().parents[2]
        cfg = OmegaConf.to_container(get_config(), resolve=True) or {}
        api_cfg = cfg.get("api", {})
        api_key = api_cfg.get("key")
        if not api_key:
            raise RuntimeError(
                f"Missing OpenAI API key. Set api.key in config.yml or the {API_KEY_ENV_VAR} env var."
            )

        model_name = api_cfg.get("model", "gpt5-nano")
        provider = api_cfg.get("provider", "openai")
        init_kwargs = {
            "model": model_name,
            "model_provider": provider,
            "api_key": api_key,
        }
        organization = api_cfg.get("organization")
        if organization:
            init_kwargs["organization"] = organization

        self.base_model = init_chat_model(**init_kwargs)
        self.backend = FilesystemBackend(root_dir=self.workspace_root, virtual_mode=False)
        self.tools = [self._create_move_file_tool()]
        self.agent = create_deep_agent(
            model=self.base_model,
            tools=self.tools,
            backend=self.backend,
            interrupt_on={"write_todos": True},
        )

    def _create_move_file_tool(self):
        root = self.workspace_root

        def move_file(
            source: str,
            destination: str,
            overwrite: bool = False,
            create_missing_dirs: bool = True,
        ) -> str:
            """
            Move a file or directory to a new destination within the workspace.

            :param source: Path to the file or directory to move.
            :param destination: Destination path or directory.
            :param overwrite: If True, existing destination will be replaced.
            :param create_missing_dirs: Create destination parents if they don't exist.
            """

            def _normalize(path_str: str) -> Path:
                path = Path(path_str).expanduser()
                if not path.is_absolute():
                    path = root / path
                return path.resolve()

            try:
                src_path = _normalize(source)
                dst_path = _normalize(destination)
            except (FileNotFoundError, RuntimeError):
                return "Invalid path supplied."

            for path in (src_path, dst_path):
                try:
                    path.relative_to(root)
                except ValueError:
                    return f"Path {path} is outside the workspace."

            if not src_path.exists():
                return f"Source path {src_path} does not exist."

            final_destination = dst_path
            if dst_path.exists() and dst_path.is_dir():
                final_destination = dst_path / src_path.name

            dest_parent = final_destination.parent
            if not dest_parent.exists():
                if create_missing_dirs:
                    dest_parent.mkdir(parents=True, exist_ok=True)
                else:
                    return f"Destination directory {dest_parent} does not exist."

            if final_destination.exists():
                if not overwrite:
                    return f"Destination {final_destination} already exists."
                if final_destination.is_dir():
                    shutil.rmtree(final_destination)
                else:
                    final_destination.unlink()

            shutil.move(str(src_path), str(final_destination))
            rel_src = src_path.relative_to(root)
            rel_dest = final_destination.relative_to(root)
            return f"Moved {rel_src} -> {rel_dest}"

        return move_file

    def organize(self, root: Path, semantics: dict):
        if not isinstance(semantics, dict) or not semantics:
            raise ValueError("semantics must be a non-empty dictionary.")

        root_path = self._resolve_workspace_path(root)
        if not root_path.exists():
            raise FileNotFoundError(f"Root path {root_path} does not exist.")
        if not root_path.is_dir():
            raise NotADirectoryError(f"Root path {root_path} is not a directory.")

        semantics_blob = json.dumps(semantics, indent=2, sort_keys=True)
        relative_root = root_path.relative_to(self.workspace_root)

        task_instructions = (
            "You are a filesystem organization agent. "
            f"Your scope is limited to '{relative_root}' (full path: {root_path}). "
            "Inspect the directory, create folders based on the provided semantics, and move "
            "files or subdirectories into the correct semantic folder. Use the available "
            "filesystem tools to inspect contents and the custom `move_file` tool to relocate "
            "items.\n\n"
            "Guidelines:\n"
            "1. Operate strictly inside the scope directory.\n"
            "2. Create one folder per semantic key if it does not already exist.\n"
            "3. Move each file or subdirectory into the folder whose semantics best match it.\n"
            "4. Preserve file contents; do not delete anything.\n"
            "5. Provide a concise summary of what you moved when finished.\n\n"
            "Semantics JSON:\n"
            f"{semantics_blob}"
        )

        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": task_instructions}]},
            config={"sender": "organizer"},
        )
        print(result)

    def _resolve_workspace_path(self, path: Path | str) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.workspace_root / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.workspace_root)
        except ValueError as exc:
            raise ValueError(f"Path {resolved} is outside the workspace.") from exc
        return resolved


def main():
    root = initialize_agent_data()
    semantics = {
        "work": "Documents related to professional projects, planning, clients, or company meetings.",
        "private": "Personal files such as travel plans, recipes, or family finances.",
    }
    agent = FileAgent()
    agent.organize(root, semantics)
    

if __name__ == "__main__":
    main()
