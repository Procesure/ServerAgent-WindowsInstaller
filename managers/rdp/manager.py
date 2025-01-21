import os
import subprocess
import shutil

from .models import *


class RDPManager:

    powershell: str = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    alias_ip: StrictStr = "127.0.0.2"
    alias_name: StrictStr = "procesure"

    def __init__(self, config: RDPConfig):

        self.config: RDPConfig = config

    def enable_rdp(self):

        """Enables Remote Desktop Protocol on the machine."""

        cmd = [
            self.powershell,
            "-Command", "Set-ItemProperty " 
            "-Path ", "'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -name 'fDenyTSConnections' "
            "-Value ", "0"
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("RDP has been enabled.")

    def create_windows_credentials(self):

        """Create Windows credentials in Credential Manager."""
        cmd = [
            self.powershell,
            "-Command",
            f"cmdkey /generic:{self.alias_ip} /user:{self.config.username} /pass:{self.config.password}"
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Credentials created for {self.alias_name}-{self.alias_ip}.")

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

    def handle_installation(self):

        """High-level method to handle the entire setup process."""

        try:

            self.enable_rdp()
            self.create_windows_credentials()
            self.update_hosts_file()

        except Exception as e:

            print(f"Installation failed: {e}")