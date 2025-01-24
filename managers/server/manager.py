import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from .models import ServerConfig
from typing import List, Union

from managers.manager import BaseManager


class ServerManager(BaseManager):

    server_program_data_path: Path = Path(BaseManager.program_data_path / "ssh")
    server_program_files_path: Path = Path(BaseManager.program_files_path / "server")
    server_config_path: Path = Path(server_program_data_path / "sshd_config")
    server_exe_path: Path = Path(server_program_files_path / "sshd.exe")


    common_installation_paths = [
        Path(r"C:\Program Files\OpenSSH-Win64"),
        Path(r"C:\Windows\System32\OpenSSH"),
        Path(r"C:\Program Files (x86)\OpenSSH"),
    ]

    def __init__(self, config: ServerConfig):
        super().__init__()
        self.config = config

    @abstractmethod
    def check_if_installed(self) -> bool:
        pass

    @abstractmethod
    def install(self):
        pass

    @abstractmethod
    def add_open_ssh_to_path(self):
        pass

    @abstractmethod
    def configure_ssh_service(self):
        pass

    @abstractmethod
    def configure_firewall(self):
        pass

    @abstractmethod
    def configure_authorized_keys(self):
        pass

    @abstractmethod
    def setup_ssh_program_data(self):
        pass

    @abstractmethod
    def fix_host_file_permissions(self):
        pass

    @abstractmethod
    def update_sshd_config(self):
        pass


class WinServer2016ServerManager(ServerManager, ABC):


    def __init__(self, config: ServerConfig):
        super().__init__(config)
        self.config = config

    def check_if_installed(self) -> bool:

        if self.server_exe_path.exists():
            print("OpenSSH is already installed.")
            return True

        return False

    def download(self):

        cmd = [
            "-Command",
            f"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; "
            f"Invoke-WebRequest -Uri 'https://github.com/PowerShell/Win32-OpenSSH/releases/download/V8.6.0.0p1-Beta/OpenSSH-Win64.zip' "
            f"-OutFile '{self.program_files_path / 'openssh.zip'}'; "
            f"Expand-Archive -Path '{self.program_files_path / 'openssh.zip'}' -DestinationPath '{self.program_files_path}'; "
            f"Remove-Item -Path '{self.program_files_path / 'openssh.zip'}'"
        ]

        self.execute_command(
            cmd,
            msg_in="Starting OpenSSH installation...",
            msg_out="OpenSSH has been installed.",
            msg_error="Failed to install OpenSSH."
        )

        Path(self.program_files_path / "OpenSSH-Win64").rename(Path(self.server_program_files_path))

    def setup_ssh_program_data(self):

        self.server_program_data_path.mkdir(parents=True, exist_ok=True)
        default_config_path = Path(Path.cwd() / "managers/server/sshd_config")

        if not self.server_config_path.exists():
            shutil.copy(default_config_path, self.server_config_path)
            print(f"Moved {default_config_path} to {self.server_config_path}")

    def copy2_host_permissions_script(self):

        source_script_path = "./scripts/FixHostFilePermissions.ps1"
        target_script_path = Path(self.server_program_files_path / "FixHostFilePermissions.ps1")

        try:
            shutil.copy(source_script_path, target_script_path)
            print(f"FixHostFilePermissions.ps1 script successfully copied to {target_script_path}.")
        except Exception as e:
            print(f"Failed to copy the file: {e}")

    def install_sshd(self):

        """Install the sshd service using the OpenSSH provided PowerShell script."""

        install_script = "install-sshd.ps1"

        self.execute_command(
            [
                "-ExecutionPolicy", "Bypass",
                "-File", install_script
            ],
            msg_in=f"Installing sshd service from {install_script}...",
            msg_out="sshd service installed successfully.",
            cwd=self.server_program_files_path
        )

    def configure_firewall(self):

        rule_name = "agent-agent"
        display_name = "'Procesure Server Agent'"
        local_port = "2222"

        cmd = [
            "-Command",
            f"Get-NetFirewallRule -Name {rule_name} -ErrorAction SilentlyContinue"
        ]

        try:

            status, result = self.execute_command(
                cmd
            )

            if result.returncode == 0 and result.stdout.strip():

                print(f"Firewall rule '{rule_name}' already exists.")
                return

            print(f"Firewall rule '{rule_name}' does not exist. Creating it...")

            cmd = [
                "-Command",
                f"New-NetFirewallRule -Name {rule_name} -DisplayName {display_name} -Enabled True "
                f"-Direction Inbound -Protocol TCP -Action Allow -LocalPort {local_port}"
            ]

            self.execute_command(
                cmd,
                msg_in="Creating new firewall rule...",
                msg_out="Firewall rule created successfully.",
                msg_error="Failed to create the firewall rule."
            )

        except Exception as e:
            print(f"Error checking or configuring the firewall rule: {e}")

    def configure_authorized_keys(self):

        try:

            user_ssh_path = Path(f"C:/Users/{self.config.username}/.procesure/ssh")
            user_ssh_path.mkdir(parents=True, exist_ok=True)

            authorized_keys_path = user_ssh_path / "authorized_keys"

            if not authorized_keys_path.exists():
                authorized_keys_path.touch()

            with authorized_keys_path.open("a+") as f:
                f.seek(0)
                existing_keys = f.read()
                if self.config.public_key not in existing_keys:
                    f.write(f"{self.config.public_key}\n")

            self.execute_command(
                [
                    "icacls",
                    str(user_ssh_path),
                    "/inheritance:r",
                    "/grant:r",
                    f"{self.config.username}:F",
                ]
            )

            print(f"Configured authorized_keys for {self.config.username}.")

        except Exception as e:
            print(f"Failed to configure authorized_keys for {self.config.username}: {e}")
            raise

    def fix_host_file_permissions(self):

        fix_host_permissions_path = "FixHostFilePermissions.ps1"

        cmd = [
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command",
            f"& './/{fix_host_permissions_path}' -Confirm:$false"
        ]

        self.execute_command(
            cmd,
            msg_in="Fixing host files permission",
            msg_out="FixHostFilePermissions script executed successfully",
            cwd=self.server_program_files_path
        )

    def update_sshd_config(self):

        """Update sshd_config to adjust user-specific settings and ensure proper formatting."""

        try:

            sshd_config_path = self.server_program_data_path / "sshd_config"

            # Ensure the configuration file exists or create a default one
            if not sshd_config_path.exists():
                print(f"sshd_config not found at {sshd_config_path}, creating a new one...")
                sshd_config_path.parent.mkdir(parents=True, exist_ok=True)
                with sshd_config_path.open("w") as f:
                    f.write("# Default sshd_config generated by installer\n")

            # Create a backup of the current configuration
            sshd_config_backup = sshd_config_path.with_suffix(".bak")
            if not sshd_config_backup.exists():
                sshd_config_backup.write_text(sshd_config_path.read_text())
                print(f"Backed up sshd_config to {sshd_config_backup}")
            else:
                print(f"Backup already exists at {sshd_config_backup}, skipping backup.")

            # Read the current sshd_config
            with sshd_config_path.open("r") as f:
                config_lines = f.readlines()

            # Prepare the Match User directive with additional configurations
            match_directive = f"Match User {self.config.username}\n"
            match_settings = [
                f"       AuthorizedKeysFile {self.config.username}/.procesure/ssh/authorized_keys\n",
                "       AllowTcpForwarding yes\n",
                "       PubkeyAuthentication yes\n",
                "       PasswordAuthentication no\n"
            ]

            # Determine where to insert or update the Match User directive
            match_index = -1
            for i, line in enumerate(config_lines):
                if line.strip() == match_directive.strip():
                    match_index = i
                    break

            # Insert or update the Match User block
            if match_index == -1:
                # Insert new Match block if not found
                config_lines.append("\n")  # Ensure it starts on a new line
                config_lines.append(match_directive)
                config_lines.extend(match_settings)
            else:
                # Update existing Match block
                end_index = len(config_lines)
                for j in range(match_index + 1, len(config_lines)):
                    if config_lines[j].strip().startswith("Match "):
                        end_index = j
                        break
                config_lines[match_index + 1:end_index] = match_settings

            # Write the updated configuration back to the file
            with sshd_config_path.open("w") as f:
                f.writelines(config_lines)

            print(f"Updated Match User directive for Administrator in sshd_config.")

        except Exception as e:
            print(f"Failed to update sshd_config for Administrator: {e}")

    def create_host_keys(self):

        server_temp_key_path = Path("C:\ProgramData\ssh")
        server_temp_key_path.mkdir(exist_ok=True)

        cmd = [f".//ssh-keygen", "-A"]

        self.execute_command(
            cmd,
            msg_in="Generating all missing host keys...",
            cwd=self.server_program_files_path
        )

        try:
            for key_file in server_temp_key_path.glob("ssh_host_*"):
                destination_file = self.server_program_data_path / key_file.name
                shutil.copy(str(key_file), str(destination_file))
                print(f"Copied {key_file} to {destination_file}")
        except Exception as e:
            print(f"Failed to copy host key files: {e}")


    def handle_installation(self):

        if not self.check_if_installed():
            self.download()

        self.setup_ssh_program_data()
        self.create_host_keys()
        self.copy2_host_permissions_script()
        self.fix_host_file_permissions()
        self.configure_firewall()
        self.configure_authorized_keys()
        self.update_sshd_config()
        self.install_sshd()


