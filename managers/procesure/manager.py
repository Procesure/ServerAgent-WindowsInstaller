import os
import subprocess
import requests
import yaml
from pathlib import Path
import zipfile

from managers.base.manager import BaseManager
from .models import TCPConfig


class ProcesureManager(BaseManager):

    def __init__(
        self,
        config: TCPConfig
    ):
        super().__init__()
        self.config: TCPConfig = config

    def download_procesure(self):

        """Download and install procesure (procesure)."""

        procesure_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-windows-amd64.zip"
        procesure_zip = self.program_files_path / "procesure.zip"

        try:

            self.program_files_path.mkdir(parents=True, exist_ok=True)
            self.program_data_path.parent.mkdir(parents=True, exist_ok=True)

            if self.procesure_exe_path.exists():
                print(f"{self.procesure_exe_path} already exists. Skipping download.")
                return

            print("Downloading procesure...")
            response = requests.get(procesure_url)
            response.raise_for_status()
            with open(procesure_zip, "wb") as f:
                f.write(response.content)

            print("Extracting procesure...")

            with zipfile.ZipFile(procesure_zip, "r") as zip_ref:
                zip_ref.extractall(self.program_files_path)

            os.rename(self.program_files_path / "ngrok.exe", self.procesure_exe_path)

            procesure_zip.unlink()
            print(f"Procesure downloaded and extracted to {self.program_files_path}")

        except Exception as e:

            if procesure_zip.exists():
                procesure_zip.unlink()

            raise RuntimeError(f"Failed to download or install procesure: {e}")

    def create_tcp_config(self):
        
        """Create procesure TCP configuration file."""
        
        config = {
            "version": "3",
            "authtoken": self.config.token,
            "tunnels": {
                "tcp": {
                    "proto": "tcp",
                    "addr": 22,
                    "remote_addr": self.config.address,
                }
            },
        }

        try:
            with open(self.program_data_path, "w") as f:
                yaml.safe_dump(config, f, default_flow_style=False)
            print(f"Procesure configuration saved at {self.program_data_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to create procesure configuration: {e}")

    def create_service(self):

        """Create the Procesure service using sc command."""

        self.execute_command(
            [
                str(self.procesure_exe_path),
                "service", "install", "--config",
                str(self.server_agent_config_path)
            ],
            msg_in="Creating procesure service",
            msg_out="Service create with success"
        )

    def start_service(self):

        """Start the procesure service."""

        self.execute_command(
            [str(self.procesure_exe_path), "service", "start"],
            msg_in="Starting procesure service",
            msg_out="Procesure service has started successfully"
        )


    def delete_service(self):

        self.execute_command(
            [self.sc, "delete", "ngrok"]
        )

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

        self.download_procesure()
        self.create_tcp_config()
        self.delete_service()
        self.create_service()
        self.start_service()