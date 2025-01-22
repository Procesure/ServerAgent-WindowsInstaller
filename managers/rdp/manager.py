import os
import shutil

from pathlib import Path

from managers.manager import BaseManager
from .models import *


class RDPManager(BaseManager):

    powershell: str = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    alias_ip: StrictStr = "127.0.0.2"
    alias_name: StrictStr = "procesure"

    def __init__(self, config: RDPConfig):

        super().__init__()
        self.config: RDPConfig = config

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

    def copy_rdp_config_file(self):

        """Copies an RDP configuration file to the specified directory."""

        source_path = "../../scripts/config.rdp"
        destination_path = Path(self.program_data_path / "config.rdp")
        shutil.copy(source_path, destination_path)
        print(f"RDP configuration file copied to {destination_path}")

    def copy_start_rdp_file(self):

        """Copies an RDP configuration file to the specified directory."""

        source_path = "../../scripts/start-rdp.bat"
        destination_path = Path(self.program_data_path / "start-rdp.bat")
        shutil.copy(source_path, destination_path)
        print(f"RDP configuration file copied to {destination_path}")

    def handle_installation(self):

        """High-level method to handle the entire setup process."""

        try:

            self.enable_rdp()
            self.create_windows_credentials()
            self.update_hosts_file()
            self.add_user_to_remote_desktop_allowed_users()

        except Exception as e:

            print(f"Installation failed: {e}")