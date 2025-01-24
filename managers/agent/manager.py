import os
import requests
import yaml
import zipfile

from collections import OrderedDict
from pathlib import Path

from managers.manager import BaseManager
from .models import AgentConfig


class AgentManager(BaseManager):

    agent_exe_path: Path = Path(BaseManager.program_files_path / "agent.exe")
    agent_config_path: Path = Path(BaseManager.program_data_path / "agent-config.yml")


    def __init__(
        self,
        config: AgentConfig
    ):
        super().__init__()
        self.config: AgentConfig = config

    def download_agent(self):

        """Download and install agent (agent)."""

        procesure_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-windows-amd64.zip"
        procesure_zip = self.program_files_path / "agent.zip"

        try:

            self.program_files_path.mkdir(parents=True, exist_ok=True)
            self.program_data_path.parent.mkdir(parents=True, exist_ok=True)

            if self.procesure_exe_path.exists():
                print(f"{self.procesure_exe_path} already exists. Skipping download.")
                return

            print("Downloading agent...")
            response = requests.get(procesure_url)
            response.raise_for_status()

            with open(procesure_zip, "wb") as f:
                f.write(response.content)

            print("Extracting agent...")

            with zipfile.ZipFile(procesure_zip, "r") as zip_ref:
                zip_ref.extractall(self.program_files_path)

            os.rename(self.program_files_path / "ngrok.exe", self.procesure_exe_path)

            procesure_zip.unlink()
            print(f"Procesure downloaded and extracted to {self.program_files_path}")

        except Exception as e:

            if procesure_zip.exists():
                procesure_zip.unlink()

            raise RuntimeError(f"Failed to download or install agent: {e}")

    def create_tcp_config(self, port: int = 2222):

        """Create agent TCP configuration file."""

        # Use OrderedDict to ensure the order of keys
        config = {
            "version": "3",
            "agent": {
                "authtoken": self.config.token,
            },
            "tunnels": {
                "tcp": {
                    "proto": "tcp",
                    "addr": port,
                    "remote_addr": self.config.address,
                }
            }
        }


        try:
            with open(self.agent_config_path, "w") as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
            print(f"Procesure configuration saved at {self.agent_config_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to create agent configuration: {e}")

    def add_procesure_to_path(self):

        status, result = self.execute_command(
            ["-Command", "[System.Environment]::GetEnvironmentVariable('Path', 'User')"]
        )

        current_path = result.stdout.strip()

        if self.program_files_path in current_path:
            print(f"{self.program_files_path} is already in PATH.")
            return

        new_path = f"{current_path};{self.program_files_path}"

        self.execute_command(
            [
                "powershell",
                "-Command",
                f"[System.Environment]::SetEnvironmentVariable('Path', '{new_path}', 'User')"
            ]
        )

        print(f"Added {self.program_files_path} to PATH. Restart your terminal to apply changes.")

    def handle_installation(self):

        self.download_agent()
        self.create_tcp_config()