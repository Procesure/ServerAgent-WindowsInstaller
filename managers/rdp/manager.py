import os
import shutil
import requests
import zipfile

from pathlib import Path
from io import BytesIO

from managers.manager import BaseManager
from .models import *

from gui.logger import gui_logger


class RDPManager(BaseManager):

    class_name_intro = "=================================== Procesure RDP Manager ==================================="

    alias_ip: StrictStr = "127.0.0.2"
    alias_name: StrictStr = "procesure"

    ps_exec_tools_download_url: StrictStr = "https://download.sysinternals.com/files/PSTools.zip"

    def __init__(self, config: RDPConfig):

        super().__init__(gui_logger)
        self.config: RDPConfig = config

    def download_ps_exec_tools(self):

        self.logger.log(message="Downloading PSExec Tools...")

        try:

            response = requests.get(self.ps_exec_tools_download_url)
            response.raise_for_status()
            zip_file_bytes = BytesIO(response.content)

            with zipfile.ZipFile(zip_file_bytes) as zip_file:
                psexec_path = 'PsExec.exe'
                zip_file.extract(psexec_path, path=self.program_files_path)
            print("PSExec tools downloaded and extracted successfully.")

        except requests.RequestException as e:
            print(f"Failed to download the file: {e}")
        except zipfile.BadZipFile:
            print("The downloaded file is not a zip file or it is corrupt.")

    def enable_rdp(self):

        """Enables Remote Desktop Protocol on the machine."""

        cmd = [
            "-Command", "Set-ItemProperty " 
            "-Path ", "'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -name 'fDenyTSConnections' "
            "-Value ", "0"
        ]

        self.execute_command(
            cmd,
            msg_in="Enabling RDP on the machine.",
            msg_out="RDP has been enabled",
            msg_error="Failed to enable RDP"
        )

    def disable_single_session_restriction(self):

        """Disable the restriction of Remote Desktop Services users to a single session."""

        cmd = [
            "-Command",
            "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Terminal Services' -Name 'fSingleSessionPerUser' -Value 0"
        ]

        self.execute_command(
            cmd,
            msg_in="Disabling single session restriction for RDS users.",
            msg_out="Single session restriction disabled successfully.",
            msg_error="Failed to disable single session restriction."
        )

    def create_windows_credentials(self):

        """Create Windows credentials in Credential Manager."""

        cmd = [
            "-Command",
            f"cmdkey /generic:{self.alias_ip} /user:{self.config.username} /pass:{self.config.password}"
        ]

        self.execute_command(
            cmd,
            msg_in="Creating Windows Credentials",
            msg_out=f"Credentials created for {self.alias_name}-{self.alias_ip}."
        )

    def update_hosts_file(self):

        """Adds an entry to the Windows hosts file if it does not already exist."""

        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        alias_entry = f"{self.alias_ip} {self.alias_name}"

        try:
            alias_exists = False
            if os.path.exists(hosts_path):
                with open(hosts_path, 'r') as hosts_file:
                    alias_exists = alias_entry in hosts_file.read()

            if alias_exists:
                print(f"Alias '{self.alias_name}' already exists in the hosts file.")
            else:
                # Add the alias to the hosts file
                with open(hosts_path, 'a') as hosts_file:
                    hosts_file.write(f"\n{alias_entry}\n")
                print(f"Alias '{self.alias_name}' added to the hosts file successfully!")
        except Exception as e:
            print(f"Failed to update the hosts file: {e}")

    def add_user_to_remote_desktop_allowed_users(self):

        """Adds the user to the Remote Desktop Users group."""

        cmd = [
            "-Command",
            f"Add-LocalGroupMember -Group 'Remote Desktop Users' -Member '{self.config.username}'"
        ]

        self.execute_command(
            cmd,
            msg_in=f"Adding {self.config.username} to RDP users group.",
            msg_out=f"User '{self.config.username}' added to RDP users group."
        )

    def copy_disconnect_session_file(self):

        """Copies DisconnectSession.ps1 to ProgramFiles\Procesure."""

        source_path = Path("./scripts/DisconnectSession.ps1")
        source_path = source_path.parent.resolve() / "DisconnectSession.ps1"
        destination_path = Path(self.program_files_path / "DisconnectSession.ps1")

        self.logger.log(f"Copying DisconnectSession.ps1 file {destination_path}")

        shutil.copy(source_path, destination_path)
        self.logger.log(f"Disconnect Session file copied to {destination_path}")

    def handle_installation(self):

        """High-level method to handle the entire setup process."""

        try:

            self.enable_rdp()
            self.disable_single_session_restriction()
            self.create_windows_credentials()
            self.update_hosts_file()
            self.add_user_to_remote_desktop_allowed_users()
            self.copy_disconnect_session_file()
            self.download_ps_exec_tools()

        except Exception as e:

            self.logger.log(f"Installation failed: {e}", level="error")