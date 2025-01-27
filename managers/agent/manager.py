import os
import requests
import yaml
import zipfile

from gui.logger import GUILogger
from managers.manager import BaseManager
from .models import AgentConfig

from gui.logger import gui_logger

class AgentManager(BaseManager):

    class_name_intro = "=================================== Procesure Agent Manager ==================================="

    def __init__(
        self,
        config: AgentConfig
    ):
        super().__init__(gui_logger)
        self.config: AgentConfig = config

    def download(self):

        """Download and install agent (agent)."""

        procesure_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-windows-amd64.zip"
        procesure_zip = self.program_files_path / "agent.zip"

        try:

            if self.agent_exe_path.exists():
                self.logger.log(f"{self.agent_config_path} already exists. Skipping download.")
                return

            self.logger.log("Downloading Procesure Agent...")
            response = requests.get(procesure_url)
            response.raise_for_status()

            with open(procesure_zip, "wb") as f:
                f.write(response.content)

            self.logger.log("Extracting agent...")

            with zipfile.ZipFile(procesure_zip, "r") as zip_ref:
                zip_ref.extractall(self.program_files_path)

            os.rename(self.program_files_path / "ngrok.exe", self.agent_exe_path)

            procesure_zip.unlink()
            self.logger.log(f"Procesure downloaded and extracted to {self.program_files_path}")

        except Exception as e:

            if procesure_zip.exists():
                procesure_zip.unlink()

            raise RuntimeError(f"Failed to download or install agent: {e}")

    def create_config(self, port: int = 2222):

        """Create agent TCP configuration file."""

        self.logger.log(f"Creating agent config file in {self.agent_config_path}")

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
            self.logger.log(f"Procesure configuration saved at {self.agent_config_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to create agent configuration: {e}")

    def handle_installation(self):

        self.download()
        self.create_config()