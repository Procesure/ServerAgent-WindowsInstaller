import os
import subprocess
import requests
import yaml
from pathlib import Path
import zipfile

from .models import TCPConfig, StrictStr


class ProcesureManager:

    sc: StrictStr = r"C:\Windows\System32\sc.exe"


    def __init__(
        self,
        config: TCPConfig
    ):
        
        self.config: TCPConfig = config
        
        self._procesure_installation_path = Path("C:\Program Files\Procesure")
        self._procesure_program_data_path = Path("C:\ProgramData\Procesure\server-agent.yml")
        
        self.procesure_exe = self._procesure_installation_path / "procesure.exe"

    def download_procesure(self):
        """Download and install procesure (procesure)."""
        procesure_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-windows-amd64.zip"
        procesure_zip = self._procesure_installation_path / "procesure.zip"

        try:

            self._procesure_installation_path.mkdir(parents=True, exist_ok=True)
            self._procesure_program_data_path.parent.mkdir(parents=True, exist_ok=True)

            if self.procesure_exe.exists():
                print(f"{self.procesure_exe} already exists. Skipping download.")
                return

            print("Downloading procesure...")
            response = requests.get(procesure_url)
            response.raise_for_status()
            with open(procesure_zip, "wb") as f:
                f.write(response.content)

            print("Extracting procesure...")
            with zipfile.ZipFile(procesure_zip, "r") as zip_ref:
                zip_ref.extractall(self._procesure_installation_path)

            # Rename extracted binary
            os.rename(self._procesure_installation_path / "ngrok.exe", self.procesure_exe)

            # Clean up the zip file
            procesure_zip.unlink()
            print(f"Procesure downloaded and extracted to {self._procesure_installation_path}")

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
            with open(self._procesure_program_data_path, "w") as f:
                yaml.safe_dump(config, f, default_flow_style=False)
            print(f"Procesure configuration saved at {self._procesure_program_data_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to create procesure configuration: {e}")

    def create_service(self):

        """Create the Procesure service using sc command."""

        try:

            result = subprocess.run(
                [
                    str(self.procesure_exe),
                    "service", "install", "--config",
                    self._procesure_program_data_path
                ],
                check=True,
                capture_output=True,
                text=True
            )

            print(f"Service creation output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            print("Error details:")
            print(f"Command: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")
            print(f"Error: {e.stderr}")
            raise RuntimeError(f"Failed to set up Procesure service: {e.stderr or e.output}")

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise

    def start_service(self):

        """Start the procesure service."""

        try:

            service_name = "ngrok"

            result = subprocess.run(
                [str(self.procesure_exe), "service", "start"],
                check=True,
                capture_output=True,
                text=True,
            )

            print("Service start output:")
            print(result.stdout)
            print(result.stderr)
            print(f"Procesure service '{service_name}' has started.")

        except subprocess.CalledProcessError as e:
            print("Error details:")
            print(f"Command: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")
            print(f"Error: {e.stderr}")
            raise RuntimeError(f"Failed to start procesure service: {e.stderr or e.output}")

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise

    def delete_service(self):

        try:

            print(f"Deleting procesure service")

            subprocess.run(
                [self.sc, "delete", "ngrok"],
                check=True,
                capture_output=True,
                text=True,
            )

        except subprocess.CalledProcessError as e:

            print("Error occurred while deleting the service:")
            print(f"Command: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise

    def add_procesure_to_path(self):

        try:
            # Get the current PATH variable
            result = subprocess.run(
                ["powershell", "-Command", "[System.Environment]::GetEnvironmentVariable('Path', 'User')"],
                capture_output=True,
                text=True,
                check=True
            )
            current_path = result.stdout.strip()

            # Check if the install_path is already in PATH
            if self._procesure_installation_path in current_path:
                print(f"{self._procesure_installation_path} is already in PATH.")
                return

            # Add the install_path to the PATH variable
            new_path = f"{current_path};{self._procesure_installation_path}"
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"[System.Environment]::SetEnvironmentVariable('Path', '{new_path}', 'User')"
                ],
                check=True
            )

            print(f"Added {self._procesure_installation_path} to PATH. Restart your terminal to apply changes.")

        except subprocess.CalledProcessError as e:
            print(f"Failed to add {self._procesure_installation_path} to PATH: {e.stderr or e.output}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def handle_installation(self):

        self.download_procesure()
        self.create_tcp_config()
        self.delete_service()
        self.create_service()
        self.start_service()