import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from .models import SSHConfig
from typing import List, Union

from managers.manager import BaseManager


class OpenSSHManager(BaseManager):

    program_data_ssh: Path = Path(BaseManager.program_data_path / "ssh")

    common_installation_paths = [
        Path(r"C:\Program Files\OpenSSH-Win64"),
        Path(r"C:\Windows\System32\OpenSSH"),
        Path(r"C:\Program Files (x86)\OpenSSH"),
    ]

    def __init__(self, config: SSHConfig):
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

    def handle_installation(self):

        is_installed = self.check_if_installed()

        if not is_installed:
            self.install()
            
        self.config.open_ssh_installation_path = self.config.open_ssh_installation_path / "OpenSSH-Win64"

        self.add_open_ssh_to_path()
        self.setup_ssh_program_data()
        self.configure_firewall()
        self.configure_authorized_keys()
        self.update_sshd_config()
        self.configure_ssh_service()


class WinServer2016OpenSSHManager(OpenSSHManager, ABC):

    open_ssh_program_files_path: Path = Path(OpenSSHManager.program_files_path / "OpenSSH-Win64")
    open_ssh_program_data_path: Path = Path(OpenSSHManager.program_data_path / "ssh")

    def __init__(self, config: SSHConfig):
        super().__init__(config)
        self.config = config

    def check_if_installed(self) -> bool:

        sshd_path = self.open_ssh_program_files_path / "sshd.exe"

        if sshd_path.exists():
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

    def add_open_ssh_to_path(self):

        cmd = [
            "-Command",
            f"[Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';{self.open_ssh_program_files_path}', 'Machine')"
        ]

        self.execute_command(
            cmd,
            msg_in="Adding OpenSSH to PATH...",
            msg_out="OpenSSH path added to PATH.",
            msg_error="Failed to add OpenSSH to PATH."
        )

    def setup_ssh_program_data(self):

        self.open_ssh_program_data_path.mkdir(parents=True, exist_ok=True)
        sshd_config_path = self.open_ssh_program_data_path / "sshd_config"
        default_config_path = Path(Path.cwd() / "managers/open_ssh/sshd_config")

        if not sshd_config_path.exists():
            shutil.copy(default_config_path, sshd_config_path)
            print(f"Moved {default_config_path} to {sshd_config_path}")

    def install_sshd(self):

        """Install the sshd service using the OpenSSH provided PowerShell script."""

        install_script = self.open_ssh_program_files_path / "install-sshd.ps1"

        self.execute_command(
            [
                "-ExecutionPolicy", "Bypass",
                "-File", str(install_script)
            ],
            msg_in=f"Installing sshd service from {install_script}...",
            msg_out="sshd service installed successfully."
        )

        self.fix_host_file_permissions()

    def configure_ssh_service(self):

        """Configure the sshd service to use the custom sshd_config file and ensure it starts automatically."""

        sshd_config_path = self.open_ssh_program_data_path / "sshd_config"
        sshd_exe = self.open_ssh_program_files_path / "OpenSSH-Win64" / "sshd.exe"

        # Update the service to start with the custom configuration file

        self.execute_command(
            [
                "-Command",
                f"sc.exe config sshd binPath= '\"{sshd_exe} -f {sshd_config_path}\"' start= auto"
            ],
            msg_in="Configuring sshd service to use custom config...",
            msg_out="sshd service configured to use custom configuration."
        )

    def create_sshd_service(self):
        """Install a custom named sshd service using the specified executable and configuration file."""

        sshd_config_path = self.open_ssh_program_data_path / "sshd_config"
        sshd_exe = self.open_ssh_program_files_path / "OpenSSH-Win64" / "sshd.exe"
        custom_service_name = "procesure-ssh-server"

        bin_path = f'"{sshd_exe}" -f "{sshd_config_path}"'

        create_or_modify_service_command = f"sc.exe create {custom_service_name} binPath= {bin_path} start= auto DisplayName= \"Custom SSHD Service\""

        # Execute the command using cmd /c to ensure proper handling of the entire command line
        self.execute_command(
            ["cmd", "/c", create_or_modify_service_command],
            msg_in="Creating or modifying custom sshd service...",
            msg_out="Custom sshd service created or modified successfully."
        )

    def configure_sshd_service(self):

        """Configures the custom SSHD service to use a specific configuration file."""

        sshd_config_path = self.open_ssh_program_data_path / "sshd_config"
        sshd_exe = self.open_ssh_program_files_path / "OpenSSH-Win64" / "sshd.exe"

        custom_service_name = "procesure-ssh-server"

        bin_path_command = f'sc.exe config {custom_service_name} binPath= "{sshd_exe} -f {sshd_config_path}" start= auto'
        self.execute_command(["cmd", "/c", bin_path_command])

    def restart_sshd_service(self):

        """Restart the sshd service to apply new configurations."""

        self.execute_command(
            [
                "-Command",
                "Restart-Service -Name sshd -Force"
            ],
            msg_in="Restarting sshd service...",
            msg_out="sshd service restarted successfully.",
            msg_error="Failed to restart sshd service."
        )

    def configure_firewall(self):

        cmd = [
            "-Command ", "New-NetFirewallRule ",
            "-Name ", "sshd ",
            "-DisplayName ", "OpenSSH Server (sshd) ",
            "-Enabled ", "True ",
            "-Direction Inbound ", "-Protocol TCP ",
            "-Action ", "Allow ",
            "-LocalPort ", "2222"
        ]

        self.execute_command(
            cmd,
            msg_in="Configuring firewall for SSHD...",
            msg_out="Firewall configured for SSHD.",
            msg_error="Failed to configure firewall for SSHD."
        )

    def configure_authorized_keys(self):

        try:

            user_ssh_path = Path(f"C:/Users/{self.config.username}/.procesure/ssh")
            user_ssh_path.mkdir(parents=True, exist_ok=True)

            authorized_keys_path = user_ssh_path / "authorized_keys"

            if not authorized_keys_path.exists():
                authorized_keys_path.touch()

            # Append the public key if it's not already in the file
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

        fix_host_permissions_path = self.open_ssh_program_files_path / "FixHostFilePermissions.ps1"

        self.execute_command(
            [
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                f"& '{fix_host_permissions_path}' -Confirm:$false"
            ],
            msg_in="Fixing host files permission",
            msg_out="FixHostFilePermissions script executed successfully"
        )

    def update_sshd_config(self):

        """Update sshd_config to adjust user-specific settings and ensure proper formatting."""

        try:

            sshd_config_path = self.open_ssh_program_data_path / "sshd_config"

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
            match_directive = "Match User Administrator\n"
            match_settings = [
                "       AuthorizedKeysFile Administrator/.procesure/ssh/authorized_keys\n",
                "       Port 2222\n",
                "       TCPForwarding yes\n",
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

    def handle_installation(self):

        if not self.check_if_installed():
            self.download()

        self.add_open_ssh_to_path()
        self.setup_ssh_program_data()
        self.configure_firewall()
        self.configure_authorized_keys()
        self.update_sshd_config()
        self.install_sshd()
        self.create_sshd_service()
        self.configure_ssh_service()
        self.restart_sshd_service()


    